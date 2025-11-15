"""
iTechSmart Service Catalog Engine
AI-powered automation and workflow management
"""

import asyncio
import subprocess
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import paramiko
import requests
from sqlalchemy.orm import Session

from .service_catalog_models import (
    ServiceItem, ServiceRequest, RequestApproval, RequestActivity,
    RequestAutomation, ServiceMetrics, WorkflowTemplate,
    ServiceCategory, RequestStatus, ApprovalStatus, AutomationType
)


class ServiceCatalogEngine:
    """
    AI-powered service catalog engine with automation capabilities
    """
    
    def __init__(self, db: Session, hub_url: str = None, ninja_url: str = None):
        self.db = db
        self.hub_url = hub_url or "http://hub:8000"
        self.ninja_url = ninja_url or "http://ninja:8002"
        
    # ==================== Service Item Management ====================
    
    def create_service_item(
        self,
        name: str,
        description: str,
        category: ServiceCategory,
        form_schema: Dict,
        requires_approval: bool = True,
        automation_enabled: bool = False,
        automation_script: str = None,
        automation_type: AutomationType = None,
        ai_assisted: bool = False,
        approval_workflow: List[Dict] = None,
        sla_hours: int = 24,
        user_id: int = None
    ) -> ServiceItem:
        """Create a new service catalog item"""
        
        service_item = ServiceItem(
            name=name,
            description=description,
            category=category,
            form_schema=form_schema,
            requires_approval=requires_approval,
            automation_enabled=automation_enabled,
            automation_script=automation_script,
            automation_type=automation_type,
            ai_assisted=ai_assisted,
            approval_workflow=approval_workflow or [],
            sla_hours=sla_hours,
            created_by=user_id
        )
        
        self.db.add(service_item)
        self.db.commit()
        self.db.refresh(service_item)
        
        return service_item
    
    def get_service_items_by_category(
        self,
        category: ServiceCategory = None,
        active_only: bool = True
    ) -> List[ServiceItem]:
        """Get service items by category"""
        
        query = self.db.query(ServiceItem)
        
        if category:
            query = query.filter(ServiceItem.category == category)
        
        if active_only:
            query = query.filter(ServiceItem.is_active == True)
        
        return query.order_by(ServiceItem.name).all()
    
    # ==================== Request Management ====================
    
    def create_request(
        self,
        service_item_id: int,
        requester_id: int,
        requester_email: str,
        requester_name: str,
        form_data: Dict
    ) -> ServiceRequest:
        """Create a new service request"""
        
        # Get service item
        service_item = self.db.query(ServiceItem).filter(
            ServiceItem.id == service_item_id
        ).first()
        
        if not service_item:
            raise ValueError(f"Service item {service_item_id} not found")
        
        # Generate request number
        request_number = self._generate_request_number()
        
        # Calculate due date
        due_date = datetime.utcnow() + timedelta(hours=service_item.sla_hours)
        
        # Create request
        request = ServiceRequest(
            request_number=request_number,
            service_item_id=service_item_id,
            requester_id=requester_id,
            requester_email=requester_email,
            requester_name=requester_name,
            form_data=form_data,
            status=RequestStatus.SUBMITTED,
            priority=service_item.priority,
            requires_approval=service_item.requires_approval,
            due_date=due_date
        )
        
        self.db.add(request)
        self.db.commit()
        self.db.refresh(request)
        
        # Log activity
        self._log_activity(
            request.id,
            "request_created",
            f"Request {request_number} created by {requester_name}",
            requester_id,
            requester_name
        )
        
        # Create approval workflow if needed
        if service_item.requires_approval and service_item.approval_workflow:
            self._create_approval_workflow(request, service_item.approval_workflow)
        
        # Auto-fulfill if enabled
        if service_item.auto_fulfill and not service_item.requires_approval:
            asyncio.create_task(self._auto_fulfill_request(request.id))
        
        # Send notification
        self._send_notification(request, "request_submitted")
        
        return request
    
    def _generate_request_number(self) -> str:
        """Generate unique request number"""
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        count = self.db.query(ServiceRequest).count() + 1
        return f"REQ-{timestamp}-{count:05d}"
    
    def _create_approval_workflow(
        self,
        request: ServiceRequest,
        workflow: List[Dict]
    ):
        """Create approval workflow for request"""
        
        for step_num, step in enumerate(workflow, 1):
            approval = RequestApproval(
                request_id=request.id,
                step_number=step_num,
                step_name=step.get("name", f"Step {step_num}"),
                approver_id=step.get("approver_id"),
                approver_email=step.get("approver_email"),
                approver_name=step.get("approver_name"),
                status=ApprovalStatus.PENDING if step_num == 1 else ApprovalStatus.PENDING
            )
            self.db.add(approval)
        
        request.status = RequestStatus.PENDING_APPROVAL
        self.db.commit()
        
        # Notify first approver
        first_approval = self.db.query(RequestApproval).filter(
            RequestApproval.request_id == request.id,
            RequestApproval.step_number == 1
        ).first()
        
        if first_approval:
            self._send_notification(request, "approval_requested", first_approval)
    
    # ==================== Approval Management ====================
    
    def approve_request(
        self,
        request_id: int,
        approver_id: int,
        decision_notes: str = None
    ) -> ServiceRequest:
        """Approve a service request"""
        
        request = self.db.query(ServiceRequest).filter(
            ServiceRequest.id == request_id
        ).first()
        
        if not request:
            raise ValueError(f"Request {request_id} not found")
        
        # Get current approval step
        current_approval = self.db.query(RequestApproval).filter(
            RequestApproval.request_id == request_id,
            RequestApproval.approver_id == approver_id,
            RequestApproval.status == ApprovalStatus.PENDING
        ).first()
        
        if not current_approval:
            raise ValueError("No pending approval found for this user")
        
        # Update approval
        current_approval.status = ApprovalStatus.APPROVED
        current_approval.decision_notes = decision_notes
        current_approval.decided_at = datetime.utcnow()
        
        # Log activity
        self._log_activity(
            request_id,
            "request_approved",
            f"Request approved by {current_approval.approver_name}",
            approver_id,
            current_approval.approver_name
        )
        
        # Check if all approvals are complete
        pending_approvals = self.db.query(RequestApproval).filter(
            RequestApproval.request_id == request_id,
            RequestApproval.status == ApprovalStatus.PENDING
        ).count()
        
        if pending_approvals == 0:
            # All approvals complete
            request.status = RequestStatus.APPROVED
            request.approved_at = datetime.utcnow()
            
            # Start fulfillment
            asyncio.create_task(self._start_fulfillment(request_id))
        else:
            # Notify next approver
            next_approval = self.db.query(RequestApproval).filter(
                RequestApproval.request_id == request_id,
                RequestApproval.status == ApprovalStatus.PENDING
            ).order_by(RequestApproval.step_number).first()
            
            if next_approval:
                self._send_notification(request, "approval_requested", next_approval)
        
        self.db.commit()
        self.db.refresh(request)
        
        return request
    
    def reject_request(
        self,
        request_id: int,
        approver_id: int,
        decision_notes: str
    ) -> ServiceRequest:
        """Reject a service request"""
        
        request = self.db.query(ServiceRequest).filter(
            ServiceRequest.id == request_id
        ).first()
        
        if not request:
            raise ValueError(f"Request {request_id} not found")
        
        # Get current approval
        current_approval = self.db.query(RequestApproval).filter(
            RequestApproval.request_id == request_id,
            RequestApproval.approver_id == approver_id,
            RequestApproval.status == ApprovalStatus.PENDING
        ).first()
        
        if not current_approval:
            raise ValueError("No pending approval found for this user")
        
        # Update approval
        current_approval.status = ApprovalStatus.REJECTED
        current_approval.decision_notes = decision_notes
        current_approval.decided_at = datetime.utcnow()
        
        # Update request
        request.status = RequestStatus.REJECTED
        
        # Log activity
        self._log_activity(
            request_id,
            "request_rejected",
            f"Request rejected by {current_approval.approver_name}: {decision_notes}",
            approver_id,
            current_approval.approver_name
        )
        
        # Send notification
        self._send_notification(request, "request_rejected")
        
        self.db.commit()
        self.db.refresh(request)
        
        return request
    
    # ==================== Automation & Fulfillment ====================
    
    async def _auto_fulfill_request(self, request_id: int):
        """Auto-fulfill request with automation"""
        
        request = self.db.query(ServiceRequest).filter(
            ServiceRequest.id == request_id
        ).first()
        
        if not request:
            return
        
        service_item = request.service_item
        
        if not service_item.automation_enabled:
            return
        
        # Update status
        request.status = RequestStatus.IN_PROGRESS
        request.started_at = datetime.utcnow()
        self.db.commit()
        
        # Execute automation
        await self._execute_automation(request)
    
    async def _start_fulfillment(self, request_id: int):
        """Start request fulfillment"""
        
        request = self.db.query(ServiceRequest).filter(
            ServiceRequest.id == request_id
        ).first()
        
        if not request:
            return
        
        request.status = RequestStatus.IN_PROGRESS
        request.started_at = datetime.utcnow()
        self.db.commit()
        
        # Log activity
        self._log_activity(
            request_id,
            "fulfillment_started",
            "Request fulfillment started",
            None,
            "System"
        )
        
        # Execute automation if enabled
        service_item = request.service_item
        if service_item.automation_enabled:
            await self._execute_automation(request)
        
        # Send notification
        self._send_notification(request, "fulfillment_started")
    
    async def _execute_automation(self, request: ServiceRequest):
        """Execute automation for request"""
        
        service_item = request.service_item
        
        # Create automation record
        automation = RequestAutomation(
            request_id=request.id,
            automation_type=service_item.automation_type,
            script_content=service_item.automation_script,
            ai_assisted=service_item.ai_assisted,
            started_at=datetime.utcnow()
        )
        self.db.add(automation)
        self.db.commit()
        
        try:
            # Get AI suggestions if enabled
            if service_item.ai_assisted:
                ai_suggestions = await self._get_ai_suggestions(request)
                automation.ai_suggestions = ai_suggestions
                self.db.commit()
            
            # Execute based on automation type
            if service_item.automation_type == AutomationType.POWERSHELL:
                result = await self._execute_powershell(
                    service_item.automation_script,
                    request.form_data
                )
            elif service_item.automation_type == AutomationType.BASH:
                result = await self._execute_bash(
                    service_item.automation_script,
                    request.form_data
                )
            elif service_item.automation_type == AutomationType.SSH:
                result = await self._execute_ssh(
                    service_item.automation_script,
                    request.form_data
                )
            elif service_item.automation_type == AutomationType.PYTHON:
                result = await self._execute_python(
                    service_item.automation_script,
                    request.form_data
                )
            elif service_item.automation_type == AutomationType.API_CALL:
                result = await self._execute_api_call(
                    service_item.automation_script,
                    request.form_data
                )
            elif service_item.automation_type == AutomationType.AI_AGENT:
                result = await self._execute_ai_agent(request)
            else:
                result = {"success": False, "error": "Unknown automation type"}
            
            # Update automation record
            automation.completed_at = datetime.utcnow()
            automation.success = result.get("success", False)
            automation.output = result.get("output", "")
            automation.error = result.get("error", "")
            automation.execution_time = (
                automation.completed_at - automation.started_at
            ).seconds
            
            # Update request
            if result.get("success"):
                request.status = RequestStatus.COMPLETED
                request.completed_at = datetime.utcnow()
                request.automation_executed = True
                request.automation_result = result
                
                # Log activity
                self._log_activity(
                    request.id,
                    "automation_completed",
                    "Automation completed successfully",
                    None,
                    "System"
                )
                
                # Send notification
                self._send_notification(request, "request_completed")
            else:
                request.status = RequestStatus.FAILED
                
                # Log activity
                self._log_activity(
                    request.id,
                    "automation_failed",
                    f"Automation failed: {result.get('error')}",
                    None,
                    "System"
                )
                
                # Send notification
                self._send_notification(request, "request_failed")
            
            self.db.commit()
            
        except Exception as e:
            automation.completed_at = datetime.utcnow()
            automation.success = False
            automation.error = str(e)
            request.status = RequestStatus.FAILED
            self.db.commit()
            
            # Log activity
            self._log_activity(
                request.id,
                "automation_error",
                f"Automation error: {str(e)}",
                None,
                "System"
            )
    
    async def _execute_powershell(
        self,
        script: str,
        form_data: Dict
    ) -> Dict:
        """Execute PowerShell script"""
        
        try:
            # Replace variables in script
            script = self._replace_variables(script, form_data)
            
            # Execute PowerShell
            process = await asyncio.create_subprocess_exec(
                "pwsh", "-Command", script,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            return {
                "success": process.returncode == 0,
                "output": stdout.decode(),
                "error": stderr.decode() if stderr else None
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _execute_bash(
        self,
        script: str,
        form_data: Dict
    ) -> Dict:
        """Execute Bash script"""
        
        try:
            # Replace variables in script
            script = self._replace_variables(script, form_data)
            
            # Execute Bash
            process = await asyncio.create_subprocess_shell(
                script,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            return {
                "success": process.returncode == 0,
                "output": stdout.decode(),
                "error": stderr.decode() if stderr else None
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _execute_ssh(
        self,
        script: str,
        form_data: Dict
    ) -> Dict:
        """Execute script via SSH"""
        
        try:
            # Get SSH connection details from form_data
            host = form_data.get("ssh_host")
            username = form_data.get("ssh_username")
            password = form_data.get("ssh_password")
            
            if not all([host, username, password]):
                return {"success": False, "error": "Missing SSH credentials"}
            
            # Replace variables in script
            script = self._replace_variables(script, form_data)
            
            # Connect via SSH
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(host, username=username, password=password)
            
            # Execute command
            stdin, stdout, stderr = ssh.exec_command(script)
            
            output = stdout.read().decode()
            error = stderr.read().decode()
            
            ssh.close()
            
            return {
                "success": not error,
                "output": output,
                "error": error if error else None
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _execute_python(
        self,
        script: str,
        form_data: Dict
    ) -> Dict:
        """Execute Python script"""
        
        try:
            # Replace variables in script
            script = self._replace_variables(script, form_data)
            
            # Execute Python
            exec_globals = {"form_data": form_data}
            exec(script, exec_globals)
            
            return {
                "success": True,
                "output": exec_globals.get("output", "Script executed successfully"),
                "error": None
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _execute_api_call(
        self,
        config: str,
        form_data: Dict
    ) -> Dict:
        """Execute API call"""
        
        try:
            # Parse API configuration
            api_config = json.loads(config)
            
            # Replace variables in URL and body
            url = self._replace_variables(api_config.get("url", ""), form_data)
            method = api_config.get("method", "POST")
            headers = api_config.get("headers", {})
            body = api_config.get("body", {})
            
            # Replace variables in body
            body_str = json.dumps(body)
            body_str = self._replace_variables(body_str, form_data)
            body = json.loads(body_str)
            
            # Make API call
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=body,
                timeout=30
            )
            
            return {
                "success": response.status_code < 400,
                "output": response.text,
                "error": None if response.status_code < 400 else f"HTTP {response.status_code}"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _execute_ai_agent(self, request: ServiceRequest) -> Dict:
        """Execute AI agent via Ninja"""
        
        try:
            # Call Ninja AI agent
            response = requests.post(
                f"{self.ninja_url}/api/ai/execute",
                json={
                    "task": f"Fulfill service request: {request.service_item.name}",
                    "context": {
                        "request_id": request.id,
                        "request_number": request.request_number,
                        "service_name": request.service_item.name,
                        "form_data": request.form_data
                    }
                },
                timeout=300
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": result.get("success", False),
                    "output": result.get("output", ""),
                    "error": result.get("error")
                }
            else:
                return {
                    "success": False,
                    "error": f"Ninja API error: {response.status_code}"
                }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _get_ai_suggestions(self, request: ServiceRequest) -> Dict:
        """Get AI suggestions for request fulfillment"""
        
        try:
            # Call Ninja for AI suggestions
            response = requests.post(
                f"{self.ninja_url}/api/ai/suggest",
                json={
                    "service_name": request.service_item.name,
                    "form_data": request.form_data,
                    "description": request.service_item.description
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {}
        except Exception as e:
            return {"error": str(e)}
    
    def _replace_variables(self, text: str, form_data: Dict) -> str:
        """Replace variables in text with form data"""
        
        for key, value in form_data.items():
            text = text.replace(f"{{{key}}}", str(value))
            text = text.replace(f"${{{key}}}", str(value))
        
        return text
    
    # ==================== Activity Logging ====================
    
    def _log_activity(
        self,
        request_id: int,
        activity_type: str,
        description: str,
        user_id: int = None,
        user_name: str = None
    ):
        """Log activity for request"""
        
        activity = RequestActivity(
            request_id=request_id,
            activity_type=activity_type,
            description=description,
            user_id=user_id,
            user_name=user_name
        )
        
        self.db.add(activity)
        self.db.commit()
    
    # ==================== Notifications ====================
    
    def _send_notification(
        self,
        request: ServiceRequest,
        event_type: str,
        approval: RequestApproval = None
    ):
        """Send notification for request event"""
        
        # This would integrate with iTechSmart Notify
        # For now, just log the notification
        
        notification_data = {
            "event_type": event_type,
            "request_number": request.request_number,
            "service_name": request.service_item.name,
            "requester": request.requester_name,
            "status": request.status.value
        }
        
        if approval:
            notification_data["approver"] = approval.approver_name
        
        # TODO: Call Notify API
        print(f"Notification: {event_type} - {notification_data}")
    
    # ==================== Metrics & Analytics ====================
    
    def get_request_metrics(
        self,
        service_item_id: int = None,
        start_date: datetime = None,
        end_date: datetime = None
    ) -> Dict:
        """Get request metrics"""
        
        query = self.db.query(ServiceRequest)
        
        if service_item_id:
            query = query.filter(ServiceRequest.service_item_id == service_item_id)
        
        if start_date:
            query = query.filter(ServiceRequest.created_at >= start_date)
        
        if end_date:
            query = query.filter(ServiceRequest.created_at <= end_date)
        
        total_requests = query.count()
        
        completed_requests = query.filter(
            ServiceRequest.status == RequestStatus.COMPLETED
        ).count()
        
        avg_completion_time = self.db.query(
            func.avg(
                func.extract('epoch', ServiceRequest.completed_at - ServiceRequest.submitted_at) / 3600
            )
        ).filter(
            ServiceRequest.status == RequestStatus.COMPLETED
        ).scalar() or 0
        
        return {
            "total_requests": total_requests,
            "completed_requests": completed_requests,
            "completion_rate": (completed_requests / total_requests * 100) if total_requests > 0 else 0,
            "avg_completion_time_hours": round(avg_completion_time, 2)
        }