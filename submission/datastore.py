"""Vertex AI Search tool for Betty's Bird Boutique documents."""

import logging
import os
from typing import Any

logger = logging.getLogger(__name__)

MAX_RESULTS = 5
MAX_SNIPPET_CHARS = 700


def _result_text(result: Any) -> str | None:
    """Extract a compact snippet from a Discovery Engine search result."""
    document = getattr(result, "document", None)
    if document is None:
        return None
    derived = getattr(document, "derived_struct_data", None)
    if derived is None:
        return None
    try:
        snippets = derived.get("snippets", [])
    except (AttributeError, TypeError):
        return None
    for item in snippets:
        try:
            value = item.get("snippet")
        except (AttributeError, TypeError):
            value = None
        if isinstance(value, str) and value.strip():
            label = getattr(document, "id", None) or getattr(document, "name", None)
            content = value.replace("<b>", "").replace("</b>", "").strip()
            if len(content) > MAX_SNIPPET_CHARS:
                content = content[: MAX_SNIPPET_CHARS - 1].rstrip() + "…"
            return f"[{label}] {content}" if label else content
    return None


def search(
    project_id: str,
    location: str,
    datastore_id: str,
    serving_config_id: str,
    search_query: str,
) -> list[str]:
    """Search a Discovery Engine data-store serving configuration."""
    if not all((project_id, location, datastore_id, serving_config_id)):
        raise ValueError("Vertex AI Search configuration is incomplete.")

    # Import lazily so mocked offline tests can cover error and result handling
    # even when Google client packages are not installed in the current venv.
    from google.api_core.client_options import ClientOptions
    from google.cloud import discoveryengine_v1 as discoveryengine

    client_options = (
        ClientOptions(api_endpoint=f"{location}-discoveryengine.googleapis.com")
        if location != "global"
        else None
    )
    client = discoveryengine.SearchServiceClient(client_options=client_options)
    serving_config = (
        f"projects/{project_id}/locations/{location}/collections/default_collection/"
        f"dataStores/{datastore_id}/servingConfigs/{serving_config_id}"
    )
    request = discoveryengine.SearchRequest(
        serving_config=serving_config,
        query=search_query,
        page_size=MAX_RESULTS,
        content_search_spec=discoveryengine.SearchRequest.ContentSearchSpec(
            snippet_spec=discoveryengine.SearchRequest.ContentSearchSpec.SnippetSpec(
                return_snippet=True
            )
        ),
        query_expansion_spec=discoveryengine.SearchRequest.QueryExpansionSpec(
            condition=discoveryengine.SearchRequest.QueryExpansionSpec.Condition.AUTO
        ),
        spell_correction_spec=discoveryengine.SearchRequest.SpellCorrectionSpec(
            mode=discoveryengine.SearchRequest.SpellCorrectionSpec.Mode.AUTO
        ),
    )
    response = client.search(request=request)
    results: list[str] = []
    for result in response:
        text = _result_text(result)
        if text:
            results.append(text)
        if len(results) >= MAX_RESULTS:
            break
    return results


def datastore_search_tool(search_query: str) -> list[str] | str:
    """Search indexed boutique documents for verified store-specific facts.

    Args:
        search_query: A question about boutique hours, location, history, staff,
            store birds, policies, or FAQs.

    Returns:
        A short list of retrieved snippets, or a safe status message.
    """
    if not search_query or not search_query.strip():
        return "Please provide a store-related question to search for."

    project_id = os.environ.get("VERTEX_AI_SEARCH_PROJECT_ID") or os.environ.get(
        "GOOGLE_CLOUD_PROJECT", ""
    )
    location = os.environ.get("VERTEX_AI_SEARCH_LOCATION", "")
    datastore_id = os.environ.get("VERTEX_AI_SEARCH_DATASTORE_ID", "")
    serving_config_id = os.environ.get(
        "VERTEX_AI_SEARCH_SERVING_CONFIG", "default_config"
    )
    if not all((project_id, location, datastore_id, serving_config_id)):
        return "Store information search is not configured yet."

    try:
        results = search(
            project_id=project_id,
            location=location,
            datastore_id=datastore_id,
            serving_config_id=serving_config_id,
            search_query=search_query.strip(),
        )
        return results if results else "No matching store information was found."
    except Exception as exc:
        # Do not return request details, project values, or exception text.
        logger.warning("Vertex AI Search failed (%s).", type(exc).__name__)
        return "Store information search is temporarily unavailable. Please try again later."
