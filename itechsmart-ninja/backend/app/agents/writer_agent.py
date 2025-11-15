"""
Writer Agent - Documentation, reports, and content creation
"""
from typing import Dict, Any, List, Optional
import logging

from app.agents.base_agent import BaseAgent, AgentCapability, AgentResponse

logger = logging.getLogger(__name__)


class WriterAgent(BaseAgent):
    """Agent specialized in writing documentation, reports, and content"""
    
    def __init__(self, ai_provider: str = "openai"):
        super().__init__(
            name="Writer",
            description="Specialized in creating documentation, reports, articles, and technical content",
            ai_provider=ai_provider
        )
        
        # Define capabilities
        self.capabilities = [
            AgentCapability(
                name="documentation",
                description="Generate technical documentation",
                required_tools=["ai_model"]
            ),
            AgentCapability(
                name="report_generation",
                description="Create comprehensive reports",
                required_tools=["ai_model", "data_analysis"]
            ),
            AgentCapability(
                name="content_writing",
                description="Write articles, blog posts, and content",
                required_tools=["ai_model"]
            ),
            AgentCapability(
                name="api_documentation",
                description="Generate API documentation from code",
                required_tools=["ai_model", "code_parser"]
            ),
            AgentCapability(
                name="readme_generation",
                description="Create README files for projects",
                required_tools=["ai_model"]
            ),
            AgentCapability(
                name="technical_writing",
                description="Write technical guides and tutorials",
                required_tools=["ai_model"]
            )
        ]
        
        # Supported document types
        self.supported_types = [
            "readme", "api_docs", "user_guide", "technical_guide",
            "report", "article", "blog_post", "tutorial", "changelog"
        ]
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute writing task"""
        try:
            doc_type = task.get("type", "readme")
            topic = task.get("topic", "")
            
            logger.info(f"Writer executing: {doc_type} about {topic}")
            
            if doc_type == "readme":
                result = await self._generate_readme(task)
            elif doc_type == "api_docs":
                result = await self._generate_api_docs(task)
            elif doc_type == "user_guide":
                result = await self._generate_user_guide(task)
            elif doc_type == "technical_guide":
                result = await self._generate_technical_guide(task)
            elif doc_type == "report":
                result = await self._generate_report(task)
            elif doc_type == "article":
                result = await self._generate_article(task)
            elif doc_type == "tutorial":
                result = await self._generate_tutorial(task)
            else:
                result = await self._generate_generic_content(task)
            
            # Log execution
            self.log_execution(task, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Writer execution failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "agent": self.name
            }
    
    async def _generate_readme(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Generate README.md file"""
        project_name = task.get("project_name", "Project")
        description = task.get("description", "")
        features = task.get("features", [])
        
        content = f"""# {project_name}

{description}

## Features

{self._format_list(features)}

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/{project_name.lower().replace(' ', '-')}.git

# Install dependencies
cd {project_name.lower().replace(' ', '-')}
pip install -r requirements.txt
```

## Usage

```python
# Example usage
from {project_name.lower().replace(' ', '_')} import main

main()
```

## Configuration

Create a `.env` file with the following variables:

```
API_KEY=your_api_key_here
DEBUG=False
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

For questions or support, please open an issue on GitHub.
"""
        
        return {
            "success": True,
            "content": content,
            "type": "readme",
            "format": "markdown",
            "agent": self.name
        }
    
    async def _generate_api_docs(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Generate API documentation"""
        api_name = task.get("api_name", "API")
        endpoints = task.get("endpoints", [])
        
        content = f"""# {api_name} Documentation

## Overview

This document describes the {api_name} endpoints and their usage.

## Base URL

```
https://api.example.com/v1
```

## Authentication

All API requests require authentication using an API key:

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" https://api.example.com/v1/endpoint
```

## Endpoints

"""
        
        for endpoint in endpoints:
            content += f"""### {endpoint.get('method', 'GET')} {endpoint.get('path', '/')}

{endpoint.get('description', '')}

**Parameters:**

{self._format_parameters(endpoint.get('parameters', []))}

**Response:**

```json
{endpoint.get('response_example', '{}')}
```

---

"""
        
        return {
            "success": True,
            "content": content,
            "type": "api_docs",
            "format": "markdown",
            "agent": self.name
        }
    
    async def _generate_user_guide(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Generate user guide"""
        product_name = task.get("product_name", "Product")
        sections = task.get("sections", [])
        
        content = f"""# {product_name} User Guide

## Introduction

Welcome to {product_name}! This guide will help you get started and make the most of the platform.

## Table of Contents

{self._generate_toc(sections)}

"""
        
        for section in sections:
            content += f"""## {section.get('title', 'Section')}

{section.get('content', '')}

"""
        
        return {
            "success": True,
            "content": content,
            "type": "user_guide",
            "format": "markdown",
            "agent": self.name
        }
    
    async def _generate_technical_guide(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Generate technical guide"""
        title = task.get("title", "Technical Guide")
        topic = task.get("topic", "")
        
        content = f"""# {title}

## Overview

This technical guide covers {topic} in detail.

## Prerequisites

- Basic understanding of programming concepts
- Familiarity with the command line
- Development environment setup

## Architecture

### System Components

The system consists of the following components:

1. **Backend API** - Handles all business logic
2. **Frontend** - User interface
3. **Database** - Data persistence
4. **Cache** - Performance optimization

### Data Flow

```
User → Frontend → API Gateway → Backend → Database
                                      ↓
                                   Cache
```

## Implementation

### Step 1: Setup

```bash
# Install dependencies
npm install
```

### Step 2: Configuration

Create configuration file:

```yaml
# config.yaml
database:
  host: localhost
  port: 5432
```

### Step 3: Run

```bash
# Start the application
npm start
```

## Best Practices

1. Always validate input data
2. Use environment variables for secrets
3. Implement proper error handling
4. Write comprehensive tests
5. Document your code

## Troubleshooting

### Common Issues

**Issue:** Connection timeout

**Solution:** Check network connectivity and firewall settings.

## Conclusion

This guide covered the essential aspects of {topic}. For more information, refer to the API documentation.
"""
        
        return {
            "success": True,
            "content": content,
            "type": "technical_guide",
            "format": "markdown",
            "agent": self.name
        }
    
    async def _generate_report(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive report"""
        title = task.get("title", "Report")
        data = task.get("data", {})
        
        content = f"""# {title}

**Date:** {self._get_current_date()}

## Executive Summary

This report provides an analysis of {title.lower()}.

## Key Findings

{self._format_findings(data.get('findings', []))}

## Detailed Analysis

### Metrics

{self._format_metrics(data.get('metrics', {}))}

### Trends

{self._format_trends(data.get('trends', []))}

## Recommendations

{self._format_recommendations(data.get('recommendations', []))}

## Conclusion

Based on the analysis, we recommend the following actions:

1. Implement suggested improvements
2. Monitor key metrics
3. Review progress quarterly

## Appendix

Additional data and references are available upon request.
"""
        
        return {
            "success": True,
            "content": content,
            "type": "report",
            "format": "markdown",
            "agent": self.name
        }
    
    async def _generate_article(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Generate article or blog post"""
        title = task.get("title", "Article")
        topic = task.get("topic", "")
        tone = task.get("tone", "professional")
        
        content = f"""# {title}

{self._generate_introduction(topic, tone)}

## Understanding {topic}

{self._generate_body_content(topic, tone)}

## Key Takeaways

{self._generate_takeaways(topic)}

## Conclusion

{self._generate_conclusion(topic, tone)}

---

*Published on {self._get_current_date()}*
"""
        
        return {
            "success": True,
            "content": content,
            "type": "article",
            "format": "markdown",
            "agent": self.name
        }
    
    async def _generate_tutorial(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Generate step-by-step tutorial"""
        title = task.get("title", "Tutorial")
        steps = task.get("steps", [])
        
        content = f"""# {title}

## What You'll Learn

In this tutorial, you'll learn how to {title.lower()}.

## Prerequisites

- Basic programming knowledge
- Development environment setup

## Tutorial Steps

"""
        
        for i, step in enumerate(steps, 1):
            content += f"""### Step {i}: {step.get('title', f'Step {i}')}

{step.get('description', '')}

```{step.get('language', 'bash')}
{step.get('code', '')}
```

**Expected Output:**

```
{step.get('output', '')}
```

---

"""
        
        content += """## Next Steps

Now that you've completed this tutorial, you can:

1. Explore advanced features
2. Build your own projects
3. Share your learnings

## Additional Resources

- Official documentation
- Community forums
- Video tutorials
"""
        
        return {
            "success": True,
            "content": content,
            "type": "tutorial",
            "format": "markdown",
            "agent": self.name
        }
    
    async def _generate_generic_content(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Generate generic content"""
        title = task.get("title", "Document")
        content_type = task.get("type", "document")
        
        content = f"""# {title}

This is a {content_type} about {title}.

## Content

[Content will be generated based on specific requirements]

## Conclusion

This concludes the {content_type}.
"""
        
        return {
            "success": True,
            "content": content,
            "type": content_type,
            "format": "markdown",
            "agent": self.name
        }
    
    # Helper methods
    
    def _format_list(self, items: List[str]) -> str:
        """Format list items"""
        if not items:
            return "- Feature 1\n- Feature 2\n- Feature 3"
        return "\n".join(f"- {item}" for item in items)
    
    def _format_parameters(self, params: List[Dict]) -> str:
        """Format API parameters"""
        if not params:
            return "No parameters required."
        
        result = "| Name | Type | Required | Description |\n"
        result += "|------|------|----------|-------------|\n"
        
        for param in params:
            result += f"| {param.get('name', '')} | {param.get('type', '')} | {param.get('required', 'No')} | {param.get('description', '')} |\n"
        
        return result
    
    def _generate_toc(self, sections: List[Dict]) -> str:
        """Generate table of contents"""
        if not sections:
            return ""
        
        toc = ""
        for i, section in enumerate(sections, 1):
            title = section.get('title', f'Section {i}')
            anchor = title.lower().replace(' ', '-')
            toc += f"{i}. [{title}](#{anchor})\n"
        
        return toc
    
    def _format_findings(self, findings: List[str]) -> str:
        """Format findings"""
        if not findings:
            return "- Key finding 1\n- Key finding 2\n- Key finding 3"
        return "\n".join(f"- {finding}" for finding in findings)
    
    def _format_metrics(self, metrics: Dict[str, Any]) -> str:
        """Format metrics"""
        if not metrics:
            return "No metrics available."
        
        result = "| Metric | Value |\n|--------|-------|\n"
        for key, value in metrics.items():
            result += f"| {key} | {value} |\n"
        
        return result
    
    def _format_trends(self, trends: List[str]) -> str:
        """Format trends"""
        if not trends:
            return "No trends identified."
        return "\n".join(f"- {trend}" for trend in trends)
    
    def _format_recommendations(self, recommendations: List[str]) -> str:
        """Format recommendations"""
        if not recommendations:
            return "1. Continue monitoring\n2. Implement improvements\n3. Review regularly"
        return "\n".join(f"{i}. {rec}" for i, rec in enumerate(recommendations, 1))
    
    def _get_current_date(self) -> str:
        """Get current date"""
        from datetime import datetime
        return datetime.now().strftime("%B %d, %Y")
    
    def _generate_introduction(self, topic: str, tone: str) -> str:
        """Generate introduction"""
        return f"In this article, we'll explore {topic} and its implications. " \
               f"Understanding {topic} is crucial for modern development practices."
    
    def _generate_body_content(self, topic: str, tone: str) -> str:
        """Generate body content"""
        return f"{topic} represents an important concept in software development. " \
               f"By understanding and applying these principles, developers can create " \
               f"more efficient and maintainable solutions."
    
    def _generate_takeaways(self, topic: str) -> str:
        """Generate key takeaways"""
        return f"- {topic} is essential for modern development\n" \
               f"- Implementation requires careful planning\n" \
               f"- Best practices should be followed\n" \
               f"- Continuous learning is important"
    
    def _generate_conclusion(self, topic: str, tone: str) -> str:
        """Generate conclusion"""
        return f"In conclusion, {topic} plays a vital role in software development. " \
               f"By following the guidelines and best practices outlined in this article, " \
               f"you can effectively implement {topic} in your projects."