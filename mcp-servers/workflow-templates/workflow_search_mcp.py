#!/usr/bin/env python3
"""MCP server for searching n8n workflow templates."""

import json
import logging
import os
from typing import Dict, List, Any
import asyncio

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import httpx

# Configuration
API_URL = os.getenv("TEMPLATE_API_URL", "http://localhost:8000/api")
TIMEOUT = int(os.getenv("SEARCH_TIMEOUT", "5000")) / 1000

# Setup logging
log_level = os.getenv("LOG_LEVEL", "ERROR").upper()
logging.basicConfig(
    level=getattr(logging, log_level, logging.ERROR),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class WorkflowTemplateServer:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=TIMEOUT)
        
    async def search_templates(
        self, 
        query: str, 
        category: str = None, 
        trigger_type: str = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Search workflow templates."""
        try:
            response = await self.client.post(
                f"{API_URL}/search",
                json={
                    "query": query,
                    "category": category,
                    "trigger_type": trigger_type,
                    "limit": limit
                }
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []
            
    async def get_template_metadata(self, template_id: str) -> Dict[str, Any]:
        """Get detailed template metadata."""
        try:
            response = await self.client.get(f"{API_URL}/template/{template_id}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Metadata error: {e}")
            return None
            
    async def list_categories(self) -> Dict[str, Any]:
        """List all categories."""
        try:
            response = await self.client.get(f"{API_URL}/categories")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Categories error: {e}")
            return {"categories": []}
            
    async def list_popular_templates(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get popular templates."""
        try:
            response = await self.client.get(
                f"{API_URL}/popular",
                params={"limit": limit}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Popular templates error: {e}")
            return []

# Create server instance
server = Server("workflow-templates")
template_server = WorkflowTemplateServer()

@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List available tools."""
    return [
        Tool(
            name="search_templates",
            description="Search n8n workflow templates by query, category, or trigger type",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (searches name, description, services)"
                    },
                    "category": {
                        "type": "string",
                        "description": "Filter by category (e.g., 'AI', 'Data Processing')"
                    },
                    "trigger_type": {
                        "type": "string",
                        "description": "Filter by trigger type (e.g., 'webhook', 'schedule')"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum results to return",
                        "default": 20
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_template_metadata",
            description="Get detailed metadata for a specific workflow template",
            inputSchema={
                "type": "object",
                "properties": {
                    "template_id": {
                        "type": "string",
                        "description": "Template ID"
                    }
                },
                "required": ["template_id"]
            }
        ),
        Tool(
            name="list_categories",
            description="List all available workflow categories with counts",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="list_popular_templates",
            description="Get most popular workflow templates",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Number of templates to return",
                        "default": 10
                    }
                }
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls."""
    try:
        if name == "search_templates":
            results = await template_server.search_templates(**arguments)
            return [TextContent(
                type="text",
                text=json.dumps(results, indent=2)
            )]
            
        elif name == "get_template_metadata":
            metadata = await template_server.get_template_metadata(
                arguments["template_id"]
            )
            return [TextContent(
                type="text",
                text=json.dumps(metadata, indent=2) if metadata else "Template not found"
            )]
            
        elif name == "list_categories":
            categories = await template_server.list_categories()
            return [TextContent(
                type="text",
                text=json.dumps(categories, indent=2)
            )]
            
        elif name == "list_popular_templates":
            templates = await template_server.list_popular_templates(
                arguments.get("limit", 10)
            )
            return [TextContent(
                type="text",
                text=json.dumps(templates, indent=2)
            )]
            
        else:
            return [TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]
            
    except Exception as e:
        logger.error(f"Tool execution error: {e}")
        return [TextContent(
            type="text",
            text=f"Error executing {name}: {str(e)}"
        )]

# Run server
async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="workflow-templates",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())