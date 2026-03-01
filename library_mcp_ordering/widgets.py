"""
Widget definitions and HTML templates
"""

import logging
from typing import Any, Dict

import mcp.types as types

from library_mcp_ordering.models import BurgerWidget

logger = logging.getLogger(__name__)

MIME_TYPE = "text/html+skybridge"

# Define the burger display widget
burger_widget = BurgerWidget(
    identifier="burger-display",
    title="Show Burger",
    template_uri="ui://widget/burger-display.html",
    invoking="Preparing your burger selection",
    invoked="Burger menu ready",
    html=(
        "<div id=\"burger-root\"></div>\n"
        "<script>\n"
        "  (function() {\n"
        "    const root = document.getElementById('burger-root');\n"
        "    \n"
        "    // Get burger data from structured content\n"
        "    const burgerData = window.__WIDGET_DATA__ || {};\n"
        "    const burgers = burgerData.burgers || [];\n"
        "    \n"
        "    // Create burger cards\n"
        "    root.innerHTML = `\n"
        "      <style>\n"
        "        #burger-root {\n"
        "          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;\n"
        "          padding: 20px;\n"
        "          max-width: 1200px;\n"
        "          margin: 0 auto;\n"
        "        }\n"
        "        .burger-grid {\n"
        "          display: grid;\n"
        "          grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));\n"
        "          gap: 20px;\n"
        "          margin-top: 20px;\n"
        "        }\n"
        "        .burger-card {\n"
        "          border: 1px solid #e0e0e0;\n"
        "          border-radius: 12px;\n"
        "          overflow: hidden;\n"
        "          background: white;\n"
        "          box-shadow: 0 2px 8px rgba(0,0,0,0.1);\n"
        "          transition: transform 0.2s, box-shadow 0.2s;\n"
        "        }\n"
        "        .burger-card:hover {\n"
        "          transform: translateY(-4px);\n"
        "          box-shadow: 0 4px 16px rgba(0,0,0,0.15);\n"
        "        }\n"
        "        .burger-image {\n"
        "          width: 100%;\n"
        "          height: 200px;\n"
        "          object-fit: cover;\n"
        "          background: #f5f5f5;\n"
        "        }\n"
        "        .burger-content {\n"
        "          padding: 16px;\n"
        "        }\n"
        "        .burger-name {\n"
        "          font-size: 18px;\n"
        "          font-weight: 600;\n"
        "          margin: 0 0 8px 0;\n"
        "          color: #333;\n"
        "        }\n"
        "        .burger-description {\n"
        "          font-size: 14px;\n"
        "          color: #666;\n"
        "          margin: 0 0 12px 0;\n"
        "          line-height: 1.4;\n"
        "        }\n"
        "        .burger-meta {\n"
        "          display: flex;\n"
        "          justify-content: space-between;\n"
        "          align-items: center;\n"
        "          margin-top: 12px;\n"
        "          padding-top: 12px;\n"
        "          border-top: 1px solid #eee;\n"
        "        }\n"
        "        .burger-price {\n"
        "          font-size: 20px;\n"
        "          font-weight: 700;\n"
        "          color: #2ecc71;\n"
        "        }\n"
        "        .burger-calories {\n"
        "          font-size: 13px;\n"
        "          color: #999;\n"
        "        }\n"
        "        .burger-ingredients {\n"
        "          display: flex;\n"
        "          flex-wrap: wrap;\n"
        "          gap: 6px;\n"
        "          margin-top: 8px;\n"
        "        }\n"
        "        .ingredient-tag {\n"
        "          background: #f0f0f0;\n"
        "          padding: 4px 8px;\n"
        "          border-radius: 4px;\n"
        "          font-size: 11px;\n"
        "          color: #666;\n"
        "        }\n"
        "        .result-count {\n"
        "          font-size: 16px;\n"
        "          color: #666;\n"
        "          margin-bottom: 10px;\n"
        "        }\n"
        "      </style>\n"
        "      <div class=\"result-count\">\n"
        "        Found ${burgers.length} burger${burgers.length !== 1 ? 's' : ''}\n"
        "      </div>\n"
        "      <div class=\"burger-grid\">\n"
        "        ${burgers.map(burger => `\n"
        "          <div class=\"burger-card\">\n"
        "            <img class=\"burger-image\" src=\"${burger.thumbnail}\" alt=\"${burger.name}\" />\n"
        "            <div class=\"burger-content\">\n"
        "              <h3 class=\"burger-name\">${burger.name}</h3>\n"
        "              <p class=\"burger-description\">${burger.description}</p>\n"
        "              <div class=\"burger-ingredients\">\n"
        "                ${burger.ingredients.map(ing => \n"
        "                  `<span class=\"ingredient-tag\">${ing}</span>`\n"
        "                ).join('')}\n"
        "              </div>\n"
        "              <div class=\"burger-meta\">\n"
        "                <span class=\"burger-price\">$${burger.price.toFixed(2)}</span>\n"
        "                <span class=\"burger-calories\">${burger.calories} cal</span>\n"
        "              </div>\n"
        "            </div>\n"
        "          </div>\n"
        "        `).join('')}\n"
        "      </div>\n"
        "    `;\n"
        "  })();\n"
        "</script>"
    ),
)


def _tool_meta(widget: BurgerWidget) -> Dict[str, Any]:
    """Generate tool metadata for a widget."""
    return {
        "openai/outputTemplate": widget.template_uri,
        "openai/toolInvocation/invoking": widget.invoking,
        "openai/toolInvocation/invoked": widget.invoked,
        "openai/widgetAccessible": True,
        "openai/resultCanProduceWidget": True,
        "annotations": {
            "destructiveHint": False,
            "openWorldHint": False,
            "readOnlyHint": True,
        }
    }


def _embedded_widget_resource(widget: BurgerWidget) -> types.EmbeddedResource:
    """Create an embedded widget resource."""
    return types.EmbeddedResource(
        type="resource",
        resource=types.TextResourceContents(
            uri=widget.template_uri,
            mimeType=MIME_TYPE,
            text=widget.html,
            title=widget.title,
        ),
    )


logger.info("Widget configuration loaded")
