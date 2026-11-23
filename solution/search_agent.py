from pathlib import Path

from google.adk import Agent
from google.adk.tools import google_search, AgentTool
from google.genai.types import GenerateContentConfig, HttpOptions, HttpRetryOptions

# Definition of an agent tool that accesses Grounding with Google Search

# Read the instructions from a file in the same
# directory as this file.
instruction = Path(__file__).with_name("search-prompt.txt").read_text(encoding="utf-8")

# Gemini 2.5 Flash supports the ADK Google Search grounding tool and gives concise
# research responses with lower latency and cost than a larger reasoning model.
model = "gemini-2.5-flash"

tools = [
    google_search
]

search_with_grounding_agent = Agent(
    name="search_with_grounding",
    description="An agent that can search the web for bird information.",
    instruction=instruction,
    model=model,
    tools=tools,
    generate_content_config=GenerateContentConfig(
        http_options=HttpOptions(
            retry_options=HttpRetryOptions(initial_delay=1, attempts=3),
        )
    )
)

search_with_grounding = AgentTool(agent=search_with_grounding_agent)
