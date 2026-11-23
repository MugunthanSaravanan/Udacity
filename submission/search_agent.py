"""Bird research sub-agent using ADK's Google Search grounding tool."""

import os
from pathlib import Path

from google.adk import Agent
from google.adk.tools import AgentTool, google_search
from google.genai.types import GenerateContentConfig, HttpOptions, HttpRetryOptions

instruction = Path(__file__).with_name("search-prompt.txt").read_text(encoding="utf-8")

# Match the user-reported successful Vertex AI model and global location.
# Runtime compatibility with the locally installed ADK cannot be checked until
# the missing Google dependencies are available in the project's virtualenv.
model = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash-lite")

search_with_grounding_agent = Agent(
    name="bird_web_research_agent",
    description="Researches general bird questions using grounded Google Search results.",
    instruction=instruction,
    model=model,
    tools=[google_search],
    generate_content_config=GenerateContentConfig(
        http_options=HttpOptions(retry_options=HttpRetryOptions(initial_delay=1, attempts=3))
    ),
)

# Google Search stays isolated in this one-tool specialist; propagate its citations
# and grounding metadata through the tool response when supported by ADK.
search_with_grounding = AgentTool(
    agent=search_with_grounding_agent,
    propagate_grounding_metadata=True,
)
