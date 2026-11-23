"""Root ADK agent for Betty's Bird Boutique."""

import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from google.adk import Agent
from google.adk.sessions import InMemorySessionService
from google.genai.types import GenerateContentConfig, HttpOptions, HttpRetryOptions
from toolbox_core import ToolboxSyncClient

try:  # Support both ADK package loading and direct module imports in local checks.
    from .datastore import datastore_search_tool
    from .search_agent import search_with_grounding
except ImportError:
    from datastore import datastore_search_tool
    from search_agent import search_with_grounding

logger = logging.getLogger(__name__)
load_dotenv(Path(__file__).with_name(".env"))

# ADK web uses an in-memory session service for short-term, per-session context.
# Keep this instance available for local runners that construct their own Runner.
session_service = InMemorySessionService()

instruction = Path(__file__).with_name("agent-prompt.txt").read_text(encoding="utf-8")


def _toolbox_unavailable(name: str) -> str:
    """Look up a product's current price by name when Toolbox is available."""
    logger.warning("Toolbox product lookup is unavailable.")
    return "Product pricing is temporarily unavailable. Please try again later."


def _load_product_lookup():
    toolbox_url = os.environ.get("TOOLBOX_URL", "http://127.0.0.1:5000")
    try:
        return ToolboxSyncClient(toolbox_url).load_tool("get_product_by_name")
    except Exception as exc:
        # Avoid logging endpoint details, which can contain sensitive configuration.
        logger.warning("Could not load Toolbox product lookup (%s).", type(exc).__name__)
        return _toolbox_unavailable


# Gemini 2.5 Flash is a fast, cost-conscious model suitable for customer support
# tool routing and concise answers; it also supports ADK's Google Search grounding flow.
model = "gemini-2.5-flash"
root_agent = Agent(
    name="bettys_bird_boutique_agent",
    description="Customer service for Betty's Bird Boutique and general bird questions.",
    instruction=instruction,
    model=model,
    tools=[_load_product_lookup(), datastore_search_tool, search_with_grounding],
    generate_content_config=GenerateContentConfig(
        http_options=HttpOptions(retry_options=HttpRetryOptions(initial_delay=1, attempts=3))
    ),
)
