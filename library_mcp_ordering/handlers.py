"""
MCP request handlers
"""

from __future__ import annotations

import logging
from copy import deepcopy
from typing import Any, Dict, List

import mcp.types as types
from pydantic import ValidationError

from library_mcp_ordering.filters import filter_burgers
from library_mcp_ordering.models import TOOL_INPUT_SCHEMA, BurgerFilterInput
from library_mcp_ordering.widgets import (
    MIME_TYPE,
    _embedded_widget_resource,
    _tool_meta,
    burger_widget,
)

logger = logging.getLogger(__name__)


async def _list_tools() -> List[types.Tool]:
    """List available tools."""
    logger.info("Listing tools")
    return [
        types.Tool(
            name="search-burgers",
            title="Search Burgers",
            description="Search and filter burgers by ingredients, price, and calories",
            inputSchema=deepcopy(TOOL_INPUT_SCHEMA),
            _meta=_tool_meta(burger_widget),
        )
    ]


async def _list_resources() -> List[types.Resource]:
    """List available resources."""
    logger.info("Listing resources")
    return [
        types.Resource(
            name=burger_widget.title,
            title=burger_widget.title,
            uri=burger_widget.template_uri,
            description="Burger display widget markup",
            mimeType=MIME_TYPE,
            _meta=_tool_meta(burger_widget),
        )
    ]


async def _list_resource_templates() -> List[types.ResourceTemplate]:
    """List available resource templates."""
    logger.info("Listing resource templates")
    return [
        types.ResourceTemplate(
            name=burger_widget.title,
            title=burger_widget.title,
            uriTemplate=burger_widget.template_uri,
            description="Burger display widget markup",
            mimeType=MIME_TYPE,
            _meta=_tool_meta(burger_widget),
        )
    ]


async def _handle_read_resource(req: types.ReadResourceRequest) -> types.ServerResult:
    """Handle resource read requests."""
    logger.info(f"Reading resource: {req.params.uri}")

    if str(req.params.uri) != burger_widget.template_uri:
        logger.warning(f"Unknown resource requested: {req.params.uri}")
        return types.ServerResult(
            types.ReadResourceResult(
                contents=[],
                _meta={"error": f"Unknown resource: {req.params.uri}"},
            )
        )

    contents = [
        types.TextResourceContents(
            uri=burger_widget.template_uri,
            mimeType=MIME_TYPE,
            text=burger_widget.html,
            _meta=_tool_meta(burger_widget),
        )
    ]

    logger.info("Resource read successfully")
    return types.ServerResult(types.ReadResourceResult(contents=contents))


async def _call_tool_request(req: types.CallToolRequest) -> types.ServerResult:
    """Handle tool call requests."""
    logger.info(f"Tool called: {req.params.name}")

    if req.params.name != "search-burgers":
        logger.error(f"Unknown tool: {req.params.name}")
        return types.ServerResult(
            types.CallToolResult(
                content=[
                    types.TextContent(
                        type="text",
                        text=f"Unknown tool: {req.params.name}",
                    )
                ],
                isError=True,
            )
        )

    arguments = req.params.arguments or {}
    logger.info(f"Tool arguments: {arguments}")

    try:
        payload = BurgerFilterInput.model_validate(arguments)
    except ValidationError as exc:
        logger.error(f"Input validation error: {exc.errors()}")
        return types.ServerResult(
            types.CallToolResult(
                content=[
                    types.TextContent(
                        type="text",
                        text=f"Input validation error: {exc.errors()}",
                    )
                ],
                isError=True,
            )
        )

    # Filter burgers
    filtered_burgers = filter_burgers(
        ingredient=payload.ingredient,
        max_price=payload.max_price,
        max_calories=payload.max_calories
    )

    # Build response text
    if not filtered_burgers:
        response_text = "No burgers found matching your criteria."
        logger.info("No burgers matched the criteria")
    else:
        response_text = f"Found {len(filtered_burgers)} burger(s) matching your criteria."
        logger.info(f"Found {len(filtered_burgers)} matching burgers")

    # Prepare widget data
    widget_resource = _embedded_widget_resource(burger_widget)
    meta: Dict[str, Any] = {
        "openai.com/widget": widget_resource.model_dump(mode="json"),
        "openai/outputTemplate": burger_widget.template_uri,
        "openai/toolInvocation/invoking": burger_widget.invoking,
        "openai/toolInvocation/invoked": burger_widget.invoked,
        "openai/widgetAccessible": True,
        "openai/resultCanProduceWidget": True,
    }

    logger.info("Tool execution completed successfully")
    return types.ServerResult(
        types.CallToolResult(
            content=[
                types.TextContent(
                    type="text",
                    text=response_text,
                )
            ],
            structuredContent={"burgers": filtered_burgers},
            _meta=meta,
        )
    )
