"""Offline configuration tests; no Google Search request is made here."""

import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOLUTION = PROJECT_ROOT / "solution"
if not SOLUTION.exists():  # The same tests also run from submission/tests.
    SOLUTION = PROJECT_ROOT
sys.path.insert(0, str(SOLUTION))

from search_agent import search_with_grounding_agent  # noqa: E402
from google.adk.tools import google_search  # noqa: E402


class TestSearchAgentConfiguration(unittest.TestCase):
    def test_search_agent_is_configured_for_bird_research(self):
        self.assertEqual(search_with_grounding_agent.name, "search_with_grounding")
        self.assertIn("Google Search grounding tool", search_with_grounding_agent.instruction)
        self.assertIn("bird-related", search_with_grounding_agent.instruction)
        self.assertIn(google_search, search_with_grounding_agent.tools)

    def test_root_agent_tool_wrapper_exists(self):
        from search_agent import search_with_grounding

        self.assertIsNotNone(search_with_grounding)


if __name__ == "__main__":
    unittest.main()
