"""
MCP server setup and configuration

Uses Streamable HTTP transport (the /mcp endpoint) as required by
Mistral Le Chat for tool discovery. SSE is deprecated by Mistral.
"""

import logging

import mcp.types as types
from fastmcp import FastMCP

from library_mcp_ordering.handlers import (
    _call_tool_request,
    _handle_read_resource,
    _list_resource_templates,
    _list_resources,
    _list_tools,
)

logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("Burger MCP Server")

logger.info("Initializing MCP server")


# Register handlers
@mcp._mcp_server.list_tools()
async def list_tools_handler():
    """Handler for listing tools."""
    return await _list_tools()


@mcp._mcp_server.list_resources()
async def list_resources_handler():
    """Handler for listing resources."""
    return await _list_resources()


@mcp._mcp_server.list_resource_templates()
async def list_resource_templates_handler():
    """Handler for listing resource templates."""
    return await _list_resource_templates()


# Register custom request handlers
mcp._mcp_server.request_handlers[types.CallToolRequest] = _call_tool_request
mcp._mcp_server.request_handlers[types.ReadResourceRequest] = _handle_read_resource

logger.info("MCP server configured and ready")
