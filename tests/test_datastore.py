"""Offline tests for datastore tool routing and safe error handling."""

import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOLUTION = PROJECT_ROOT / "solution"
if not SOLUTION.exists():  # The same tests also run from submission/tests.
    SOLUTION = PROJECT_ROOT
sys.path.insert(0, str(SOLUTION))

from datastore import datastore_search_tool  # noqa: E402


class TestDatastoreTool(unittest.TestCase):
    @patch("datastore.search", return_value=["The shop is open Monday to Friday."])
    def test_returns_matching_document_text(self, mock_search):
        with patch.dict(os.environ, {"DATASTORE_PROJECT_ID": "test-project", "DATASTORE_ENGINE_ID": "test-engine", "DATASTORE_LOCATION": "global"}):
            result = datastore_search_tool("What are the store hours?")
        self.assertEqual(result, ["The shop is open Monday to Friday."])
        mock_search.assert_called_once_with(
            project_id="test-project",
            location="global",
            engine_id="test-engine",
            search_query="What are the store hours?",
        )

    @patch("datastore.search", return_value=[])
    def test_empty_results_are_reported(self, _mock_search):
        with patch.dict(os.environ, {"DATASTORE_PROJECT_ID": "test-project", "DATASTORE_ENGINE_ID": "test-engine", "DATASTORE_LOCATION": "global"}):
            self.assertEqual(datastore_search_tool("unknown fact"), "No results found.")

    @patch("datastore.search", side_effect=RuntimeError("sensitive request detail"))
    def test_errors_do_not_leak_exception_text(self, _mock_search):
        with patch.dict(os.environ, {"DATASTORE_PROJECT_ID": "test-project", "DATASTORE_ENGINE_ID": "test-engine", "DATASTORE_LOCATION": "global"}):
            result = datastore_search_tool("store hours")
        self.assertIn("temporarily unavailable", result)
        self.assertNotIn("sensitive request detail", result)

    def test_blank_query_does_not_call_service(self):
        with patch("datastore.search") as mock_search:
            self.assertIn("provide", datastore_search_tool("  "))
        mock_search.assert_not_called()


if __name__ == "__main__":
    unittest.main()
