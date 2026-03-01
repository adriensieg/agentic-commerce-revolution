"""
Burger MCP Server with Widget Support for Mistral Le Chat
Provides burger filtering and querying with visual widgets
Uses Streamable HTTP transport (/mcp) for Le Chat tool discovery
"""

import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
logger.info("Initializing library_mcp_ordering package")

from library_mcp_ordering.server import mcp

__all__ = ["mcp"]

logger.info("library_mcp_ordering package initialized successfully")
