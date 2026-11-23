"""Root ADK agent for Betty's Bird Boutique."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).with_name(".env"))

from google.adk import Agent
from google.adk.sessions import InMemorySessionService
from google.genai.types import GenerateContentConfig, HttpOptions, HttpRetryOptions

try:  # Support ADK package loading and direct module imports.
    from .datastore import datastore_search_tool
    from .product_tool import load_product_lookup
    from .search_agent import search_with_grounding
except ImportError:
    from datastore import datastore_search_tool
    from product_tool import load_product_lookup
    from search_agent import search_with_grounding

APP_NAME = "bettys_bird_boutique"

# User-provided Vocareum configuration: Gemini 3.5 Flash-Lite was reported to
# return a successful response in project lab18633938-1795419661 at location global.
# This is a model identifier string; ADK delegates model validation to google-genai.
model = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash-lite")

# ADK local runners use this service to keep short-term session history in memory.
session_service = InMemorySessionService()
instruction = Path(__file__).with_name("agent-prompt.txt").read_text(encoding="utf-8")

toolbox_url = os.environ.get("TOOLBOX_URL", "http://127.0.0.1:5000")
product_lookup_tool = load_product_lookup(toolbox_url)

root_agent = Agent(
    name="bettys_bird_boutique_agent",
    description=(
        "Customer service for Betty's Bird Boutique, its products and store facts, "
        "and general bird questions."
    ),
    instruction=instruction,
    model=model,
    tools=[product_lookup_tool, datastore_search_tool, search_with_grounding],
    generate_content_config=GenerateContentConfig(
        http_options=HttpOptions(retry_options=HttpRetryOptions(initial_delay=1, attempts=3))
    ),
)
