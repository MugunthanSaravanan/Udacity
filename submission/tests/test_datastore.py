"""Offline tests for datastore configuration and result handling."""

import os
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT))

from datastore import _result_text, datastore_search_tool  # noqa: E402


class TestDatastoreTool(unittest.TestCase):
    def setUp(self):
        self.environment = {
            "GOOGLE_CLOUD_PROJECT": "lab-project",
            "VERTEX_AI_SEARCH_LOCATION": "global",
            "VERTEX_AI_SEARCH_DATASTORE_ID": "sample-store",
            "VERTEX_AI_SEARCH_SERVING_CONFIG": "default_config",
        }

    @patch("datastore.search", return_value=["[hours] Open Tuesday through Saturday."])
    def test_successful_retrieval_uses_configured_datastore(self, mock_search):
        with patch.dict(os.environ, self.environment, clear=True):
            result = datastore_search_tool("What are the store hours?")
        self.assertEqual(result, ["[hours] Open Tuesday through Saturday."])
        mock_search.assert_called_once_with(
            project_id="lab-project",
            location="global",
            datastore_id="sample-store",
            serving_config_id="default_config",
            search_query="What are the store hours?",
        )

    @patch("datastore.search", return_value=[])
    def test_empty_results_are_reported(self, _mock_search):
        with patch.dict(os.environ, self.environment, clear=True):
            result = datastore_search_tool("unlisted store fact")
        self.assertIn("No matching", result)

    @patch("datastore.search", side_effect=RuntimeError("private request detail"))
    def test_api_failure_is_safe(self, _mock_search):
        with patch.dict(os.environ, self.environment, clear=True):
            result = datastore_search_tool("store hours")
        self.assertIn("temporarily unavailable", result)
        self.assertNotIn("private request detail", result)

    def test_missing_configuration_does_not_call_service(self):
        with patch.dict(os.environ, {}, clear=True), patch("datastore.search") as mock_search:
            result = datastore_search_tool("store hours")
        self.assertIn("not configured", result)
        mock_search.assert_not_called()

    def test_blank_query_does_not_call_service(self):
        with patch.dict(os.environ, self.environment, clear=True), patch("datastore.search") as mock_search:
            self.assertIn("provide", datastore_search_tool("  "))
        mock_search.assert_not_called()

    def test_extracts_and_bounds_document_snippet(self):
        snippet = "A" * 800
        result = _result_text(
            SimpleNamespace(
                document=SimpleNamespace(
                    id="hours-doc",
                    name="",
                    derived_struct_data={"snippets": [{"snippet": f"Store <b>{snippet}</b>"}]},
                )
            )
        )
        self.assertTrue(result.startswith("[hours-doc] Store "))
        self.assertLessEqual(len(result), 800)
        self.assertNotIn("<b>", result)


if __name__ == "__main__":
    unittest.main()
