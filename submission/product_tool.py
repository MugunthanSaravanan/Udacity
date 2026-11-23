"""Safe wrapper for the product lookup served by MCP Toolbox."""

import logging
from collections.abc import Callable
from typing import Any

logger = logging.getLogger(__name__)


def _unavailable_tool(name: str) -> str:
    """Return a safe response when the product database cannot be reached."""
    return "Product pricing is temporarily unavailable. Please try again later."


def load_product_lookup(
    toolbox_url: str,
    client_factory: Callable[[str], Any] | None = None,
) -> Callable[[str], str]:
    """Load a Toolbox product tool and hide remote connection error details.

    Args:
        toolbox_url: Local or approved MCP Toolbox endpoint.
        client_factory: Optional client constructor for offline tests.

    Returns:
        An ADK-compatible function that searches product names.
    """
    try:
        if client_factory is None:
            from toolbox_core import ToolboxSyncClient

            client_factory = ToolboxSyncClient
        remote_tool = client_factory(toolbox_url).load_tool("get_product_by_name")
    except Exception as exc:
        logger.warning("Could not load Toolbox product lookup (%s).", type(exc).__name__)
        return _unavailable_tool

    def get_product_by_name(name: str) -> str:
        """Find a product by full or partial name and return its database details.

        Args:
            name: Full or partial product name.
        """
        if not name or not name.strip():
            return "Please provide a product name to search for."
        try:
            result = remote_tool(name=name.strip())
        except Exception as exc:
            logger.warning("Toolbox product lookup failed (%s).", type(exc).__name__)
            return "Product pricing is temporarily unavailable. Please try again later."
        if result is None or result == "" or result == [] or result == {}:
            return "No matching product was found in the product database."
        return result if isinstance(result, str) else str(result)

    return get_product_by_name
