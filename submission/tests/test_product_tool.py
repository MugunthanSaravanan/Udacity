"""Offline tests for the MCP Toolbox product lookup wrapper."""

import unittest
from pathlib import Path
from unittest.mock import Mock

from product_tool import load_product_lookup


class FakeToolboxClient:
    def __init__(self, url, result="Bird Seed Mix: 15.99", error=None):
        self.url = url
        self.result = result
        self.error = error
        self.loaded_name = None

    def load_tool(self, name):
        self.loaded_name = name

        def call_tool(*, name):
            if self.error:
                raise self.error
            return self.result

        return call_tool


class TestProductLookup(unittest.TestCase):
    def make_factory(self, **client_args):
        created = []

        def factory(url):
            client = FakeToolboxClient(url, **client_args)
            created.append(client)
            return client

        return factory, created

    def test_product_search_loads_named_tool_and_returns_result(self):
        factory, created = self.make_factory(result="Bird Seed Mix: 15.99")
        lookup = load_product_lookup("http://toolbox.test:5000", client_factory=factory)
        self.assertEqual(lookup("  Bird Seed  "), "Bird Seed Mix: 15.99")
        self.assertEqual(created[0].url, "http://toolbox.test:5000")
        self.assertEqual(created[0].loaded_name, "get_product_by_name")

    def test_partial_name_is_passed_to_parameterized_tool(self):
        captured = {}

        class Client:
            def load_tool(self, tool_name):
                def tool(*, name):
                    captured["tool_name"] = tool_name
                    captured["name"] = name
                    return "Sunflower Seeds: 22.50"

                return tool

        lookup = load_product_lookup("http://toolbox.test", client_factory=lambda _url: Client())
        self.assertIn("22.50", lookup("sunflower"))
        self.assertEqual(captured, {"tool_name": "get_product_by_name", "name": "sunflower"})

    def test_not_found_result_is_reported(self):
        factory, _created = self.make_factory(result="")
        lookup = load_product_lookup("http://toolbox.test", client_factory=factory)
        self.assertIn("No matching product", lookup("unknown"))

    def test_database_error_does_not_leak_exception_detail(self):
        factory, _created = self.make_factory(error=RuntimeError("secret connection string"))
        lookup = load_product_lookup("http://toolbox.test", client_factory=factory)
        result = lookup("finch food")
        self.assertIn("temporarily unavailable", result)
        self.assertNotIn("secret connection string", result)

    def test_toolbox_connection_failure_returns_callable_fallback(self):
        def fail_to_connect(_url):
            raise OSError("private endpoint detail")

        lookup = load_product_lookup("http://toolbox.test", client_factory=fail_to_connect)
        result = lookup("millet")
        self.assertIn("temporarily unavailable", result)
        self.assertNotIn("private endpoint detail", result)

    def test_empty_query_is_not_sent_to_toolbox(self):
        remote = Mock(return_value="should not run")
        lookup = load_product_lookup(
            "http://toolbox.test",
            client_factory=lambda _url: type("Client", (), {"load_tool": lambda _self, _name: remote})(),
        )
        self.assertIn("provide a product name", lookup(" "))
        remote.assert_not_called()

    def test_sql_uses_existing_columns_and_parameterized_wildcards(self):
        sql = (Path(__file__).resolve().parents[1] / "tools.yaml").read_text(encoding="utf-8")
        schema = (Path(__file__).resolve().parents[1] / "docs" / "betty_db.sql").read_text(encoding="utf-8")
        for column in ("id", "product_name", "price"):
            self.assertIn(column, schema)
            self.assertIn(column, sql)
        self.assertIn("LIKE CONCAT('%', ?, '%')", sql)
        self.assertNotIn("stock", schema.lower())
        self.assertNotIn("description", schema.lower())


if __name__ == "__main__":
    unittest.main()
