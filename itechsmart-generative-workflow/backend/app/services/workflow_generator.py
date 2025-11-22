import asyncio
import logging
import uuid
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import openai
from dataclasses import dataclass

from app.core.config import settings
from app.core.database import get_database
from app.services.service_discovery import ServiceDiscovery

logger = logging.getLogger(__name__)


@dataclass
class WorkflowConfig:
    """Configuration for workflow generation"""

    max_steps: int = 50
    confidence_threshold: float = 0.85
    timeout_seconds: int = 60
    max_tokens: int = 4000
    model_temperature: float = 0.3


class WorkflowGenerator:
    """AI-powered workflow generation engine"""

    def __init__(self, service_discovery: ServiceDiscovery):
        self.service_discovery = service_discovery
        self.config = WorkflowConfig()
        self.db = None
        self._initialized = False

        # Initialize OpenAI if API key is provided
        if hasattr(settings, "OPENAI_API_KEY") and settings.OPENAI_API_KEY:
            openai.api_key = settings.OPENAI_API_KEY
        else:
            logger.warning("⚠️ OpenAI API key not configured, using mock generation")

    async def initialize(self):
        """Initialize the workflow generator"""
        try:
            self.db = get_database()
            self._initialized = True
            logger.info("🤖 Workflow Generator initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Workflow Generator: {str(e)}")
            raise

    async def generate_from_text(
        self, description: str, context: Dict[str, Any] = None, refine: bool = False
    ) -> Dict[str, Any]:
        """Generate workflow from natural language description"""
        if not self._initialized:
            raise RuntimeError("Workflow generator not initialized")

        try:
            logger.info(
                f"🤖 Generating workflow from description: {description[:100]}..."
            )

            # Step 1: Parse user intent
            intent = await self._parse_intent(description, context)
            logger.info(f"📋 Intent parsed: {intent['action']} - {intent['target']}")

            # Step 2: Discover relevant services
            relevant_services = await self._discover_relevant_services(intent)
            logger.info(f"🔍 Found {len(relevant_services)} relevant services")

            # Step 3: Generate workflow steps
            workflow_steps = await self._generate_workflow_steps(
                intent, relevant_services
            )
            logger.info(f"📝 Generated {len(workflow_steps)} workflow steps")

            # Step 4: Create workflow definition
            workflow = await self._create_workflow_definition(
                description=description,
                intent=intent,
                steps=workflow_steps,
                context=context,
            )

            # Step 5: Validate and optimize
            validated_workflow = await self._validate_and_optimize(workflow)

            # Save to database
            await self._save_workflow(validated_workflow)

            logger.info(
                f"✅ Workflow generated successfully: {validated_workflow['id']}"
            )
            return validated_workflow

        except Exception as e:
            logger.error(f"❌ Error generating workflow: {str(e)}")
            raise

    async def _parse_intent(
        self, description: str, context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Parse user intent from natural language description"""

        # Use OpenAI for intent parsing if available
        if hasattr(settings, "OPENAI_API_KEY") and settings.OPENAI_API_KEY:
            try:
                prompt = f"""
                Analyze the following user request and extract the intent:
                
                Request: "{description}"
                
                Extract:
                1. Primary action (verb)
                2. Target system/entity
                3. Required parameters
                4. Conditions/triggers
                5. Expected outcome
                
                Respond in JSON format:
                {{
                    "action": "string",
                    "target": "string",
                    "parameters": ["list"],
                    "conditions": ["list"],
                    "outcome": "string",
                    "confidence": 0.95
                }}
                """

                response = await openai.ChatCompletion.acreate(
                    model="gpt-4-turbo",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an expert at parsing user intent for workflow automation.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    temperature=self.config.model_temperature,
                    max_tokens=500,
                )

                intent = json.loads(response.choices[0].message.content)
                intent["raw_description"] = description
                return intent

            except Exception as e:
                logger.warning(
                    f"⚠️ OpenAI intent parsing failed, using fallback: {str(e)}"
                )

        # Fallback to rule-based parsing
        return self._fallback_intent_parsing(description, context)

    def _fallback_intent_parsing(
        self, description: str, context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Fallback intent parsing using rule-based approach"""
        description_lower = description.lower()

        # Extract action
        actions = [
            "create",
            "update",
            "delete",
            "deploy",
            "monitor",
            "notify",
            "onboard",
            "offboard",
            "run",
            "execute",
        ]
        action = None
        for act in actions:
            if act in description_lower:
                action = act
                break

        # Extract target
        targets = [
            "user",
            "server",
            "application",
            "database",
            "workflow",
            "alert",
            "incident",
            "report",
        ]
        target = None
        for tgt in targets:
            if tgt in description_lower:
                target = tgt
                break

        # Extract common iTechSmart products
        products = [
            "passport",
            "ninja",
            "sentinel",
            "cloud",
            "notify",
            "teams",
            "connect",
            "vault",
        ]
        mentioned_products = [
            product for product in products if product in description_lower
        ]

        return {
            "action": action or "automate",
            "target": target or "system",
            "parameters": [],
            "conditions": [],
            "outcome": description,
            "confidence": 0.6,
            "raw_description": description,
            "mentioned_products": mentioned_products,
        }

    async def _discover_relevant_services(
        self, intent: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Discover iTechSmart services relevant to the intent"""
        try:
            # Get all available services
            all_services = await self.service_discovery.get_services()

            relevant_services = []

            # Match services based on intent and mentioned products
            mentioned_products = intent.get("mentioned_products", [])
            action = intent.get("action", "")
            target = intent.get("target", "")

            for service in all_services:
                service_name = service.get("name", "").lower()
                service_actions = [
                    action.lower() for action in service.get("actions", [])
                ]

                # Check if service is explicitly mentioned
                if any(product in service_name for product in mentioned_products):
                    relevant_services.append(service)
                    continue

                # Check if service actions match intent
                if any(action in service_actions for action in [action, target]):
                    relevant_services.append(service)
                    continue

                # Check for keyword matching in service capabilities
                capabilities = " ".join(service.get("capabilities", [])).lower()
                if any(keyword in capabilities for keyword in [action, target]):
                    relevant_services.append(service)

            # Limit to top 10 most relevant services
            relevant_services.sort(
                key=lambda x: x.get("relevance_score", 0), reverse=True
            )
            return relevant_services[:10]

        except Exception as e:
            logger.error(f"❌ Error discovering services: {str(e)}")
            return []

    async def _generate_workflow_steps(
        self, intent: Dict[str, Any], relevant_services: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate workflow steps based on intent and available services"""

        # Use OpenAI for step generation if available
        if hasattr(settings, "OPENAI_API_KEY") and settings.OPENAI_API_KEY:
            try:
                return await self._ai_generate_steps(intent, relevant_services)
            except Exception as e:
                logger.warning(f"⚠️ AI step generation failed, using fallback: {str(e)}")

        # Fallback to template-based generation
        return await self._template_generate_steps(intent, relevant_services)

    async def _ai_generate_steps(
        self, intent: Dict[str, Any], relevant_services: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate workflow steps using AI"""

        # Prepare service information for AI
        services_info = []
        for service in relevant_services:
            services_info.append(
                {
                    "name": service["name"],
                    "id": service["id"],
                    "actions": service["actions"],
                    "capabilities": service["capabilities"],
                }
            )

        prompt = f"""
        Generate a workflow to achieve the following intent:
        
        Intent: {json.dumps(intent, indent=2)}
        
        Available iTechSmart Services:
        {json.dumps(services_info, indent=2)}
        
        Generate a sequence of workflow steps that:
        1. Logically flow from one to the next
        2. Use appropriate services for each step
        3. Include error handling
        4. Have clear input/output mappings
        5. Include dependencies between steps
        
        Return in JSON format:
        {{
            "steps": [
                {{
                    "id": "step-1",
                    "name": "Human readable step name",
                    "service": "service-id",
                    "action": "service-action",
                    "description": "What this step does",
                    "input_mapping": {{"param1": "{{intent_param}}"}},
                    "output_mapping": {{"result": "step_output"}},
                    "depends_on": [],
                    "timeout": 30000,
                    "retry_policy": {{"max_retries": 3, "backoff": "exponential"}}
                }}
            ]
        }}
        """

        response = await openai.ChatCompletion.acreate(
            model="gpt-4-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert workflow designer for iTechSmart automation platform.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=self.config.model_temperature,
            max_tokens=self.config.max_tokens,
        )

        result = json.loads(response.choices[0].message.content)
        steps = result.get("steps", [])

        # Validate and enhance steps
        validated_steps = []
        for i, step in enumerate(steps):
            # Ensure step has required fields
            step["id"] = step.get("id", f"step-{i+1}")
            step["order"] = i

            # Validate service exists
            service_id = step.get("service")
            if not any(s["id"] == service_id for s in relevant_services):
                logger.warning(f"⚠️ Service {service_id} not found, skipping step")
                continue

            validated_steps.append(step)

        return validated_steps

    async def _template_generate_steps(
        self, intent: Dict[str, Any], relevant_services: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate workflow steps using templates"""

        action = intent.get("action", "")
        target = intent.get("target", "")

        # Template-based step generation
        if action == "onboard" and target == "user":
            return await self._generate_onboarding_steps(relevant_services)
        elif action == "deploy" and target == "application":
            return await self._generate_deployment_steps(relevant_services)
        elif action == "monitor" or action == "alert":
            return await self._generate_monitoring_steps(relevant_services)
        else:
            return await self._generate_generic_steps(intent, relevant_services)

    async def _generate_onboarding_steps(
        self, services: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate employee onboarding workflow steps"""
        steps = []

        # Step 1: Create user account
        passport_service = next(
            (s for s in services if "passport" in s["name"].lower()), None
        )
        if passport_service:
            steps.append(
                {
                    "id": "step-1",
                    "name": "Create User Account",
                    "service": passport_service["id"],
                    "action": "create_user",
                    "description": "Create user account in identity system",
                    "input_mapping": {
                        "name": "{{employee_name}}",
                        "email": "{{email}}",
                        "role": "{{role}}",
                    },
                    "output_mapping": {"user_id": "created_user_id"},
                    "depends_on": [],
                    "timeout": 30000,
                    "retry_policy": {"max_retries": 3, "backoff": "exponential"},
                }
            )

        # Step 2: Provision cloud access
        cloud_service = next(
            (s for s in services if "cloud" in s["name"].lower()), None
        )
        if cloud_service:
            steps.append(
                {
                    "id": "step-2",
                    "name": "Provision Cloud Access",
                    "service": cloud_service["id"],
                    "action": "create_access",
                    "description": "Provision cloud platform access",
                    "input_mapping": {
                        "user_id": "{{step-1.user_id}}",
                        "permissions": "{{role}}_permissions",
                    },
                    "output_mapping": {"access_id": "cloud_access_id"},
                    "depends_on": ["step-1"],
                    "timeout": 45000,
                    "retry_policy": {"max_retries": 3, "backoff": "exponential"},
                }
            )

        # Step 3: Add to collaboration tools
        connect_service = next(
            (s for s in services if "connect" in s["name"].lower()), None
        )
        if connect_service:
            steps.append(
                {
                    "id": "step-3",
                    "name": "Add to Collaboration Tools",
                    "service": connect_service["id"],
                    "action": "add_user",
                    "description": "Add user to team collaboration platforms",
                    "input_mapping": {
                        "user_id": "{{step-1.user_id}}",
                        "email": "{{email}}",
                        "teams": ["default", "{{role}}"],
                    },
                    "output_mapping": {"membership_id": "collab_membership"},
                    "depends_on": ["step-1"],
                    "timeout": 30000,
                    "retry_policy": {"max_retries": 3, "backoff": "exponential"},
                }
            )

        # Step 4: Send welcome notification
        notify_service = next(
            (s for s in services if "notify" in s["name"].lower()), None
        )
        if notify_service:
            steps.append(
                {
                    "id": "step-4",
                    "name": "Send Welcome Notification",
                    "service": notify_service["id"],
                    "action": "send_welcome",
                    "description": "Send welcome message to new employee",
                    "input_mapping": {
                        "email": "{{email}}",
                        "name": "{{employee_name}}",
                        "start_date": "{{start_date}}",
                    },
                    "output_mapping": {"notification_id": "welcome_notification"},
                    "depends_on": ["step-1", "step-2", "step-3"],
                    "timeout": 15000,
                    "retry_policy": {"max_retries": 3, "backoff": "exponential"},
                }
            )

        return steps

    async def _generate_deployment_steps(
        self, services: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate application deployment workflow steps"""
        steps = []

        # Step 1: Run pre-deployment checks
        sentinel_service = next(
            (s for s in services if "sentinel" in s["name"].lower()), None
        )
        if sentinel_service:
            steps.append(
                {
                    "id": "step-1",
                    "name": "Pre-deployment Health Check",
                    "service": sentinel_service["id"],
                    "action": "health_check",
                    "description": "Run health checks before deployment",
                    "input_mapping": {
                        "target_environment": "{{target_env}}",
                        "services": "{{target_services}}",
                    },
                    "output_mapping": {"health_status": "pre_deployment_health"},
                    "depends_on": [],
                    "timeout": 60000,
                    "retry_policy": {"max_retries": 2, "backoff": "linear"},
                }
            )

        # Step 2: Deploy application
        ninja_service = next(
            (s for s in services if "ninja" in s["name"].lower()), None
        )
        if ninja_service:
            steps.append(
                {
                    "id": "step-2",
                    "name": "Deploy Application",
                    "service": ninja_service["id"],
                    "action": "deploy",
                    "description": "Deploy application to target environment",
                    "input_mapping": {
                        "artifact": "{{deployment_artifact}}",
                        "environment": "{{target_env}}",
                        "config": "{{deployment_config}}",
                    },
                    "output_mapping": {"deployment_id": "app_deployment"},
                    "depends_on": ["step-1"],
                    "timeout": 300000,
                    "retry_policy": {"max_retries": 1, "backoff": "exponential"},
                }
            )

        # Step 3: Post-deployment verification
        if sentinel_service:
            steps.append(
                {
                    "id": "step-3",
                    "name": "Post-deployment Verification",
                    "service": sentinel_service["id"],
                    "action": "verify_deployment",
                    "description": "Verify deployment success and health",
                    "input_mapping": {
                        "deployment_id": "{{step-2.deployment_id}}",
                        "environment": "{{target_env}}",
                    },
                    "output_mapping": {
                        "verification_result": "deployment_verification"
                    },
                    "depends_on": ["step-2"],
                    "timeout": 120000,
                    "retry_policy": {"max_retries": 3, "backoff": "exponential"},
                }
            )

        return steps

    async def _generate_monitoring_steps(
        self, services: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate monitoring workflow steps"""
        steps = []

        # Step 1: Check system metrics
        sentinel_service = next(
            (s for s in services if "sentinel" in s["name"].lower()), None
        )
        if sentinel_service:
            steps.append(
                {
                    "id": "step-1",
                    "name": "Check System Metrics",
                    "service": sentinel_service["id"],
                    "action": "get_metrics",
                    "description": "Collect current system metrics",
                    "input_mapping": {
                        "targets": "{{monitoring_targets}}",
                        "time_range": "{{time_range}}",
                    },
                    "output_mapping": {"metrics": "system_metrics"},
                    "depends_on": [],
                    "timeout": 30000,
                    "retry_policy": {"max_retries": 3, "backoff": "exponential"},
                }
            )

        # Step 2: Analyze alerts
        if sentinel_service:
            steps.append(
                {
                    "id": "step-2",
                    "name": "Analyze Alerts",
                    "service": sentinel_service["id"],
                    "action": "analyze_alerts",
                    "description": "Analyze active alerts and incidents",
                    "input_mapping": {
                        "severity": "{{alert_severity}}",
                        "time_range": "{{time_range}}",
                    },
                    "output_mapping": {"alerts": "active_alerts"},
                    "depends_on": ["step-1"],
                    "timeout": 45000,
                    "retry_policy": {"max_retries": 3, "backoff": "exponential"},
                }
            )

        # Step 3: Send notification if needed
        notify_service = next(
            (s for s in services if "notify" in s["name"].lower()), None
        )
        if notify_service:
            steps.append(
                {
                    "id": "step-3",
                    "name": "Send Monitoring Report",
                    "service": notify_service["id"],
                    "action": "send_report",
                    "description": "Send monitoring report to stakeholders",
                    "input_mapping": {
                        "metrics": "{{step-1.metrics}}",
                        "alerts": "{{step-2.alerts}}",
                        "recipients": "{{notification_recipients}}",
                    },
                    "output_mapping": {"report_id": "monitoring_report"},
                    "depends_on": ["step-1", "step-2"],
                    "timeout": 30000,
                    "retry_policy": {"max_retries": 3, "backoff": "exponential"},
                }
            )

        return steps

    async def _generate_generic_steps(
        self, intent: Dict[str, Any], services: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate generic workflow steps"""
        steps = []

        # Create a simple generic workflow
        for i, service in enumerate(services[:5]):  # Limit to 5 services
            if service.get("actions"):
                first_action = service["actions"][0]

                steps.append(
                    {
                        "id": f"step-{i+1}",
                        "name": f"Execute {service['name']} Action",
                        "service": service["id"],
                        "action": first_action,
                        "description": f"Execute {first_action} on {service['name']}",
                        "input_mapping": {"target": "{{target}}"},
                        "output_mapping": {"result": f"result_{i+1}"},
                        "depends_on": [f"step-{i}"] if i > 0 else [],
                        "timeout": 30000,
                        "retry_policy": {"max_retries": 3, "backoff": "exponential"},
                    }
                )

        return steps

    async def _create_workflow_definition(
        self,
        description: str,
        intent: Dict[str, Any],
        steps: List[Dict[str, Any]],
        context: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """Create complete workflow definition"""
        workflow_id = str(uuid.uuid4())

        # Extract input schema from steps
        input_schema = self._extract_input_schema(steps, intent)

        workflow = {
            "id": workflow_id,
            "name": f"Generated Workflow: {intent.get('action', 'Automate')} {intent.get('target', 'Task')}",
            "description": description,
            "version": "1.0.0",
            "intent": intent,
            "input_schema": input_schema,
            "steps": steps,
            "error_handling": {
                "on_failure": "notify_admin",
                "retry_strategy": "automatic",
                "timeout_handling": "escalate",
            },
            "metadata": {
                "generated_by": "iTechSmart Generative Workflow",
                "generated_at": datetime.utcnow().isoformat(),
                "context": context or {},
                "confidence": intent.get("confidence", 0.8),
            },
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }

        return workflow

    def _extract_input_schema(
        self, steps: List[Dict[str, Any]], intent: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract input schema from workflow steps"""
        schema = {}

        # Add parameters from intent
        intent_params = intent.get("parameters", [])
        for param in intent_params:
            schema[param] = "string"

        # Extract variables from step input mappings
        for step in steps:
            input_mapping = step.get("input_mapping", {})
            for value in input_mapping.values():
                # Extract template variables like {{employee_name}}
                matches = re.findall(r"\{\{([^}]+)\}\}", str(value))
                for match in matches:
                    if "." not in match:  # Skip step references like step-1.user_id
                        schema[match] = "string"

        return schema

    async def _validate_and_optimize(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and optimize the workflow"""

        # Validate step dependencies
        steps = workflow.get("steps", [])
        step_ids = [step["id"] for step in steps]

        for step in steps:
            depends_on = step.get("depends_on", [])
            for dep in depends_on:
                if dep not in step_ids:
                    logger.warning(
                        f"⚠️ Step {step['id']} depends on non-existent step {dep}"
                    )
                    # Remove invalid dependency
                    step["depends_on"].remove(dep)

        # Optimize step order based on dependencies
        optimized_steps = self._optimize_step_order(steps)
        workflow["steps"] = optimized_steps

        # Add performance optimizations
        workflow = self._add_performance_optimizations(workflow)

        return workflow

    def _optimize_step_order(self, steps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Optimize step order based on dependencies"""
        if not steps:
            return steps

        # Simple topological sort based on dependencies
        optimized = []
        remaining = steps.copy()

        while remaining:
            # Find steps with no unmet dependencies
            ready_steps = [
                step
                for step in remaining
                if all(
                    dep in [s["id"] for s in optimized]
                    for dep in step.get("depends_on", [])
                )
            ]

            if not ready_steps:
                # Circular dependency - add remaining steps as-is
                optimized.extend(remaining)
                break

            # Add ready steps
            for step in ready_steps:
                optimized.append(step)
                remaining.remove(step)

        return optimized

    def _add_performance_optimizations(
        self, workflow: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Add performance optimizations to workflow"""

        # Add parallel execution opportunities
        steps = workflow.get("steps", [])

        # Group steps that can run in parallel
        parallel_groups = []
        current_group = []

        for i, step in enumerate(steps):
            if i == 0:
                current_group.append(step)
            else:
                # Check if this step can run in parallel with current group
                can_parallel = True
                step_deps = set(step.get("depends_on", []))

                for group_step in current_group:
                    if group_step["id"] in step_deps or set(
                        group_step.get("depends_on", [])
                    ) & {step["id"]}:
                        can_parallel = False
                        break

                if can_parallel:
                    current_group.append(step)
                else:
                    parallel_groups.append(current_group)
                    current_group = [step]

        if current_group:
            parallel_groups.append(current_group)

        # Add parallel execution metadata
        workflow["execution_groups"] = parallel_groups

        return workflow

    async def _save_workflow(self, workflow: Dict[str, Any]):
        """Save workflow to database"""
        try:
            await self.db.workflows.insert_one(workflow)
            logger.info(f"💾 Workflow {workflow['id']} saved to database")
        except Exception as e:
            logger.error(f"❌ Failed to save workflow: {str(e)}")
            # Continue without saving to database

    async def refine_workflow(
        self, workflow_id: str, feedback: str, context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Refine an existing workflow based on user feedback"""
        try:
            # Get existing workflow
            existing_workflow = await self.get_workflow(workflow_id)
            if not existing_workflow:
                raise ValueError(f"Workflow {workflow_id} not found")

            logger.info(
                f"🔧 Refining workflow {workflow_id} with feedback: {feedback[:50]}..."
            )

            # Generate refined version
            refined_workflow = await self._generate_refined_workflow(
                existing_workflow, feedback, context
            )

            # Save refined version
            await self._save_workflow(refined_workflow)

            logger.info(f"✅ Workflow refined: {refined_workflow['id']}")
            return refined_workflow

        except Exception as e:
            logger.error(f"❌ Error refining workflow: {str(e)}")
            raise

    async def _generate_refined_workflow(
        self,
        existing_workflow: Dict[str, Any],
        feedback: str,
        context: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """Generate a refined version of the workflow"""

        # For now, create a new version with updated description
        refined_workflow = existing_workflow.copy()
        refined_workflow["id"] = str(uuid.uuid4())
        refined_workflow["version"] = self._increment_version(
            existing_workflow.get("version", "1.0.0")
        )
        refined_workflow["description"] = (
            f"{existing_workflow.get('description', '')}\n\nRefinement: {feedback}"
        )
        refined_workflow["refinement_feedback"] = feedback
        refined_workflow["refined_from"] = existing_workflow["id"]
        refined_workflow["created_at"] = datetime.utcnow()
        refined_workflow["updated_at"] = datetime.utcnow()

        return refined_workflow

    def _increment_version(self, version: str) -> str:
        """Increment version number"""
        try:
            parts = version.split(".")
            parts[-1] = str(int(parts[-1]) + 1)
            return ".".join(parts)
        except:
            return "2.0.0"

    async def get_workflow(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get workflow by ID"""
        try:
            workflow = await self.db.workflows.find_one({"id": workflow_id})
            return workflow
        except Exception as e:
            logger.error(f"❌ Error getting workflow: {str(e)}")
            return None

    async def update_workflow(
        self, workflow_id: str, workflow_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update workflow"""
        try:
            workflow_data["updated_at"] = datetime.utcnow()

            await self.db.workflows.update_one(
                {"id": workflow_id}, {"$set": workflow_data}
            )

            updated = await self.get_workflow(workflow_id)
            return updated

        except Exception as e:
            logger.error(f"❌ Error updating workflow: {str(e)}")
            raise

    async def delete_workflow(self, workflow_id: str):
        """Delete workflow"""
        try:
            await self.db.workflows.delete_one({"id": workflow_id})
            logger.info(f"🗑️ Workflow {workflow_id} deleted")
        except Exception as e:
            logger.error(f"❌ Error deleting workflow: {str(e)}")
            raise

    async def create_workflow(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create workflow from structured data"""
        try:
            # Generate ID if not provided
            if "id" not in workflow_data:
                workflow_data["id"] = str(uuid.uuid4())

            # Set timestamps
            workflow_data["created_at"] = datetime.utcnow()
            workflow_data["updated_at"] = datetime.utcnow()

            # Set metadata
            if "metadata" not in workflow_data:
                workflow_data["metadata"] = {}

            workflow_data["metadata"]["created_by"] = "iTechSmart Generative Workflow"
            workflow_data["metadata"]["structured_creation"] = True

            # Save workflow
            await self._save_workflow(workflow_data)

            return workflow_data

        except Exception as e:
            logger.error(f"❌ Error creating workflow: {str(e)}")
            raise

    async def get_templates(
        self, category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get workflow templates"""
        # For now, return static templates
        templates = [
            {
                "id": "template-onboarding",
                "name": "Employee Onboarding",
                "category": "hr",
                "description": "Complete employee onboarding workflow",
                "steps": 4,
                "estimated_time": "30 minutes",
            },
            {
                "id": "template-deployment",
                "name": "Application Deployment",
                "category": "devops",
                "description": "Automated application deployment",
                "steps": 3,
                "estimated_time": "15 minutes",
            },
            {
                "id": "template-incident-response",
                "name": "Incident Response",
                "category": "operations",
                "description": "Automated incident response workflow",
                "steps": 5,
                "estimated_time": "10 minutes",
            },
        ]

        if category:
            templates = [t for t in templates if t["category"] == category]

        return templates

    async def get_analytics(
        self, days: int = 30, workflow_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get workflow analytics"""
        try:
            since = datetime.utcnow() - timedelta(days=days)

            # Query for workflows
            query = {"created_at": {"$gte": since}}
            if workflow_id:
                query["id"] = workflow_id

            workflows = list(self.db.workflows.find(query))

            # Calculate analytics
            total_workflows = len(workflows)

            # Group by action type
            actions = {}
            for workflow in workflows:
                intent = workflow.get("intent", {})
                action = intent.get("action", "unknown")
                actions[action] = actions.get(action, 0) + 1

            # Calculate success metrics (mock for now)
            avg_confidence = (
                sum(w.get("metadata", {}).get("confidence", 0.5) for w in workflows)
                / total_workflows
                if total_workflows > 0
                else 0
            )

            return {
                "total_workflows": total_workflows,
                "date_range": f"Last {days} days",
                "action_distribution": actions,
                "average_confidence": round(avg_confidence, 2),
                "most_common_action": (
                    max(actions.items(), key=lambda x: x[1])[0] if actions else None
                ),
                "workflow_id_filter": workflow_id,
            }

        except Exception as e:
            logger.error(f"❌ Error getting analytics: {str(e)}")
            return {"error": str(e)}

    async def health_check(self) -> Dict[str, Any]:
        """Health check for the workflow generator"""
        return {
            "status": "healthy" if self._initialized else "uninitialized",
            "openai_configured": hasattr(settings, "OPENAI_API_KEY")
            and bool(settings.OPENAI_API_KEY),
            "database_connected": self.db is not None,
            "max_steps": self.config.max_steps,
            "confidence_threshold": self.config.confidence_threshold,
        }

    async def cleanup(self):
        """Cleanup resources"""
        self._initialized = False
        logger.info("🧹 Workflow Generator cleanup complete")
