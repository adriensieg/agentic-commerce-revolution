"""
Burger MCP Server - Main Entry Point

Exposes the MCP server via Streamable HTTP at /mcp.
This is the transport required by Mistral Le Chat for tool discovery.
SSE (/sse) is deprecated by Mistral and will not allow tools to be discovered.

Register your connector in Le Chat using:
  https://<your-domain>/mcp

Verify tool discovery manually:
  curl -sS -X POST https://<your-domain>/mcp \
    -H 'Content-Type: application/json' \
    -d '{
      "jsonrpc": "2.0",
      "id": 1,
      "method": "initialize",
      "params": {
        "protocolVersion": "2024-11-05",
        "capabilities": {}
      }
    }'
"""

import logging
import os

from starlette.requests import Request
from starlette.responses import JSONResponse

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

from library_mcp_ordering import mcp


@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> JSONResponse:
    return JSONResponse({"status": "ok"})


# Expose ASGI app for uvicorn.
# path="/mcp" uses Streamable HTTP transport — required by Mistral Le Chat.
app = mcp.http_app(path="/mcp")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    # "http" transport = Streamable HTTP (JSON-RPC over HTTP POST at /mcp)
    mcp.run(transport="http", host="0.0.0.0", port=port)