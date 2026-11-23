"""Dependency-free checks for Google Search specialist configuration and prompts."""

import unittest
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]


class TestSearchAgentConfiguration(unittest.TestCase):
    def test_specialist_isolated_and_wrapped_for_root(self):
        source = (PROJECT / "search_agent.py").read_text(encoding="utf-8")
        self.assertIn("tools=[google_search]", source)
        self.assertIn("AgentTool(", source)
        self.assertIn("agent=search_with_grounding_agent", source)
        self.assertIn("propagate_grounding_metadata=True", source)
        self.assertIn('os.environ.get("GEMINI_MODEL", "gemini-3.5-flash-lite")', source)

    def test_search_prompt_limits_scope_and_citations(self):
        prompt = (PROJECT / "search-prompt.txt").read_text(encoding="utf-8").lower()
        self.assertIn("only general bird-related questions", prompt)
        self.assertIn("ground factual answers in google search results", prompt)
        self.assertIn("never invent urls", prompt)
        self.assertIn("boutique-specific facts", prompt)

    def test_root_agent_registers_three_sources_and_reported_model_default(self):
        source = (PROJECT / "agent.py").read_text(encoding="utf-8")
        self.assertIn('os.environ.get("GEMINI_MODEL", "gemini-3.5-flash-lite")', source)
        self.assertIn("tools=[product_lookup_tool, datastore_search_tool, search_with_grounding]", source)
        self.assertIn("InMemorySessionService()", source)

    def test_prompts_disallow_orders_and_unverified_stock(self):
        prompt = (PROJECT / "agent-prompt.txt").read_text(encoding="utf-8").lower()
        self.assertIn("do not accept, place, or process orders", prompt)
        self.assertIn("never invent", prompt)
        self.assertIn("stock status", prompt)

    def test_runner_has_explicit_session_helpers(self):
        source = (PROJECT / "agents.py").read_text(encoding="utf-8")
        self.assertIn("async def create_session", source)
        self.assertIn("async def send_message", source)
        self.assertIn("await session_service.create_session", source)
        self.assertIn("session_id=session_id", source)


if __name__ == "__main__":
    unittest.main()
