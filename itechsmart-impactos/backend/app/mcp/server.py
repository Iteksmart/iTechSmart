"""
MCP Server Core Implementation
"""

import asyncio
import json
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from enum import Enum


class MCPMessageType(str, Enum):
    """MCP message types"""

    INITIALIZE = "initialize"
    INITIALIZED = "initialized"
    TOOL_CALL = "tools/call"
    TOOL_RESULT = "tools/result"
    RESOURCE_READ = "resources/read"
    RESOURCE_LIST = "resources/list"
    PROMPT_GET = "prompts/get"
    PROMPT_LIST = "prompts/list"
    ERROR = "error"
    PING = "ping"
    PONG = "pong"


class MCPServer:
    """
    Model Context Protocol Server

    Provides secure connectors for AI models to access tools, resources, and prompts
    """

    def __init__(self, name: str, version: str):
        """
        Initialize MCP Server

        Args:
            name: Server name
            version: Server version
        """
        self.name = name
        self.version = version
        self.tools: Dict[str, Dict[str, Any]] = {}
        self.resources: Dict[str, Dict[str, Any]] = {}
        self.prompts: Dict[str, Dict[str, Any]] = {}
        self.connections: Dict[str, Dict[str, Any]] = {}
        self.message_handlers: Dict[str, Callable] = {}

        # Register default handlers
        self._register_default_handlers()

    def _register_default_handlers(self):
        """Register default message handlers"""
        self.message_handlers[MCPMessageType.INITIALIZE] = self._handle_initialize
        self.message_handlers[MCPMessageType.TOOL_CALL] = self._handle_tool_call
        self.message_handlers[MCPMessageType.RESOURCE_READ] = self._handle_resource_read
        self.message_handlers[MCPMessageType.RESOURCE_LIST] = self._handle_resource_list
        self.message_handlers[MCPMessageType.PROMPT_GET] = self._handle_prompt_get
        self.message_handlers[MCPMessageType.PROMPT_LIST] = self._handle_prompt_list
        self.message_handlers[MCPMessageType.PING] = self._handle_ping

    def register_tool(
        self,
        name: str,
        description: str,
        parameters: Dict[str, Any],
        handler: Callable,
        required_permissions: Optional[List[str]] = None,
    ):
        """
        Register a tool

        Args:
            name: Tool name
            description: Tool description
            parameters: Tool parameters schema
            handler: Tool handler function
            required_permissions: Required permissions to use tool
        """
        self.tools[name] = {
            "name": name,
            "description": description,
            "parameters": parameters,
            "handler": handler,
            "required_permissions": required_permissions or [],
            "registered_at": datetime.utcnow().isoformat(),
        }

    def register_resource(
        self,
        uri: str,
        name: str,
        description: str,
        mime_type: str,
        handler: Callable,
        required_permissions: Optional[List[str]] = None,
    ):
        """
        Register a resource

        Args:
            uri: Resource URI
            name: Resource name
            description: Resource description
            mime_type: Resource MIME type
            handler: Resource handler function
            required_permissions: Required permissions to access resource
        """
        self.resources[uri] = {
            "uri": uri,
            "name": name,
            "description": description,
            "mimeType": mime_type,
            "handler": handler,
            "required_permissions": required_permissions or [],
            "registered_at": datetime.utcnow().isoformat(),
        }

    def register_prompt(
        self,
        name: str,
        description: str,
        arguments: List[Dict[str, Any]],
        template: str,
        required_permissions: Optional[List[str]] = None,
    ):
        """
        Register a prompt template

        Args:
            name: Prompt name
            description: Prompt description
            arguments: Prompt arguments
            template: Prompt template
            required_permissions: Required permissions to use prompt
        """
        self.prompts[name] = {
            "name": name,
            "description": description,
            "arguments": arguments,
            "template": template,
            "required_permissions": required_permissions or [],
            "registered_at": datetime.utcnow().isoformat(),
        }

    async def _handle_initialize(
        self, message: Dict[str, Any], connection_id: str
    ) -> Dict[str, Any]:
        """Handle initialize message"""
        client_info = message.get("params", {}).get("clientInfo", {})

        # Store connection
        self.connections[connection_id] = {
            "client_name": client_info.get("name", "unknown"),
            "client_version": client_info.get("version", "unknown"),
            "connected_at": datetime.utcnow().isoformat(),
            "permissions": message.get("params", {}).get("permissions", []),
        }

        return {
            "jsonrpc": "2.0",
            "id": message.get("id"),
            "result": {
                "protocolVersion": "2024-11-05",
                "serverInfo": {"name": self.name, "version": self.version},
                "capabilities": {
                    "tools": {"listChanged": True},
                    "resources": {"subscribe": True, "listChanged": True},
                    "prompts": {"listChanged": True},
                },
            },
        }

    async def _handle_tool_call(
        self, message: Dict[str, Any], connection_id: str
    ) -> Dict[str, Any]:
        """Handle tool call message"""
        params = message.get("params", {})
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        if tool_name not in self.tools:
            return {
                "jsonrpc": "2.0",
                "id": message.get("id"),
                "error": {"code": -32601, "message": f"Tool not found: {tool_name}"},
            }

        tool = self.tools[tool_name]

        # Check permissions
        connection = self.connections.get(connection_id, {})
        user_permissions = connection.get("permissions", [])
        required_permissions = tool.get("required_permissions", [])

        if required_permissions and not any(
            perm in user_permissions for perm in required_permissions
        ):
            return {
                "jsonrpc": "2.0",
                "id": message.get("id"),
                "error": {
                    "code": -32000,
                    "message": f"Insufficient permissions for tool: {tool_name}",
                },
            }

        try:
            # Execute tool handler
            result = await tool["handler"](arguments)

            return {
                "jsonrpc": "2.0",
                "id": message.get("id"),
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                json.dumps(result)
                                if isinstance(result, dict)
                                else str(result)
                            ),
                        }
                    ]
                },
            }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": message.get("id"),
                "error": {"code": -32000, "message": f"Tool execution error: {str(e)}"},
            }

    async def _handle_resource_read(
        self, message: Dict[str, Any], connection_id: str
    ) -> Dict[str, Any]:
        """Handle resource read message"""
        params = message.get("params", {})
        uri = params.get("uri")

        if uri not in self.resources:
            return {
                "jsonrpc": "2.0",
                "id": message.get("id"),
                "error": {"code": -32601, "message": f"Resource not found: {uri}"},
            }

        resource = self.resources[uri]

        # Check permissions
        connection = self.connections.get(connection_id, {})
        user_permissions = connection.get("permissions", [])
        required_permissions = resource.get("required_permissions", [])

        if required_permissions and not any(
            perm in user_permissions for perm in required_permissions
        ):
            return {
                "jsonrpc": "2.0",
                "id": message.get("id"),
                "error": {
                    "code": -32000,
                    "message": f"Insufficient permissions for resource: {uri}",
                },
            }

        try:
            # Execute resource handler
            content = await resource["handler"]()

            return {
                "jsonrpc": "2.0",
                "id": message.get("id"),
                "result": {
                    "contents": [
                        {
                            "uri": uri,
                            "mimeType": resource["mimeType"],
                            "text": (
                                content
                                if isinstance(content, str)
                                else json.dumps(content)
                            ),
                        }
                    ]
                },
            }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": message.get("id"),
                "error": {"code": -32000, "message": f"Resource read error: {str(e)}"},
            }

    async def _handle_resource_list(
        self, message: Dict[str, Any], connection_id: str
    ) -> Dict[str, Any]:
        """Handle resource list message"""
        connection = self.connections.get(connection_id, {})
        user_permissions = connection.get("permissions", [])

        # Filter resources by permissions
        accessible_resources = []
        for uri, resource in self.resources.items():
            required_permissions = resource.get("required_permissions", [])
            if not required_permissions or any(
                perm in user_permissions for perm in required_permissions
            ):
                accessible_resources.append(
                    {
                        "uri": uri,
                        "name": resource["name"],
                        "description": resource["description"],
                        "mimeType": resource["mimeType"],
                    }
                )

        return {
            "jsonrpc": "2.0",
            "id": message.get("id"),
            "result": {"resources": accessible_resources},
        }

    async def _handle_prompt_get(
        self, message: Dict[str, Any], connection_id: str
    ) -> Dict[str, Any]:
        """Handle prompt get message"""
        params = message.get("params", {})
        prompt_name = params.get("name")
        arguments = params.get("arguments", {})

        if prompt_name not in self.prompts:
            return {
                "jsonrpc": "2.0",
                "id": message.get("id"),
                "error": {
                    "code": -32601,
                    "message": f"Prompt not found: {prompt_name}",
                },
            }

        prompt = self.prompts[prompt_name]

        # Check permissions
        connection = self.connections.get(connection_id, {})
        user_permissions = connection.get("permissions", [])
        required_permissions = prompt.get("required_permissions", [])

        if required_permissions and not any(
            perm in user_permissions for perm in required_permissions
        ):
            return {
                "jsonrpc": "2.0",
                "id": message.get("id"),
                "error": {
                    "code": -32000,
                    "message": f"Insufficient permissions for prompt: {prompt_name}",
                },
            }

        # Render template with arguments
        template = prompt["template"]
        for key, value in arguments.items():
            template = template.replace(f"{{{key}}}", str(value))

        return {
            "jsonrpc": "2.0",
            "id": message.get("id"),
            "result": {
                "description": prompt["description"],
                "messages": [
                    {"role": "user", "content": {"type": "text", "text": template}}
                ],
            },
        }

    async def _handle_prompt_list(
        self, message: Dict[str, Any], connection_id: str
    ) -> Dict[str, Any]:
        """Handle prompt list message"""
        connection = self.connections.get(connection_id, {})
        user_permissions = connection.get("permissions", [])

        # Filter prompts by permissions
        accessible_prompts = []
        for name, prompt in self.prompts.items():
            required_permissions = prompt.get("required_permissions", [])
            if not required_permissions or any(
                perm in user_permissions for perm in required_permissions
            ):
                accessible_prompts.append(
                    {
                        "name": name,
                        "description": prompt["description"],
                        "arguments": prompt["arguments"],
                    }
                )

        return {
            "jsonrpc": "2.0",
            "id": message.get("id"),
            "result": {"prompts": accessible_prompts},
        }

    async def _handle_ping(
        self, message: Dict[str, Any], connection_id: str
    ) -> Dict[str, Any]:
        """Handle ping message"""
        return {"jsonrpc": "2.0", "id": message.get("id"), "result": {}}

    async def handle_message(
        self, message: Dict[str, Any], connection_id: str
    ) -> Dict[str, Any]:
        """
        Handle incoming MCP message

        Args:
            message: MCP message
            connection_id: Connection ID

        Returns:
            Response message
        """
        method = message.get("method")

        if method not in self.message_handlers:
            return {
                "jsonrpc": "2.0",
                "id": message.get("id"),
                "error": {"code": -32601, "message": f"Method not found: {method}"},
            }

        handler = self.message_handlers[method]
        return await handler(message, connection_id)

    def get_stats(self) -> Dict[str, Any]:
        """Get server statistics"""
        return {
            "name": self.name,
            "version": self.version,
            "tools_count": len(self.tools),
            "resources_count": len(self.resources),
            "prompts_count": len(self.prompts),
            "active_connections": len(self.connections),
            "uptime": "N/A",  # TODO: Track uptime
        }
