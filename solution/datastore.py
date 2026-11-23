"""Vertex AI Search tool for Betty's Bird Boutique documents."""

import logging
import os

from google.api_core.client_options import ClientOptions
from google.cloud import discoveryengine_v1 as discoveryengine

logger = logging.getLogger(__name__)


def search(project_id: str, location: str, engine_id: str, search_query: str) -> list[str]:
    """Search a Discovery Engine app serving configuration and return chunk text."""
    if not all((project_id, location, engine_id)):
        raise ValueError("Vertex AI Search configuration is incomplete.")

    client_options = (
        ClientOptions(api_endpoint=f"{location}-discoveryengine.googleapis.com")
        if location != "global"
        else None
    )
    client = discoveryengine.SearchServiceClient(client_options=client_options)
    serving_config = (
        f"projects/{project_id}/locations/{location}/collections/default_collection/"
        f"engines/{engine_id}/servingConfigs/default_config"
    )
    request = discoveryengine.SearchRequest(
        serving_config=serving_config,
        query=search_query,
        page_size=10,
        content_search_spec=discoveryengine.SearchRequest.ContentSearchSpec(
            search_result_mode=discoveryengine.SearchRequest.ContentSearchSpec.SearchResultMode.CHUNKS
        ),
        query_expansion_spec=discoveryengine.SearchRequest.QueryExpansionSpec(
            condition=discoveryengine.SearchRequest.QueryExpansionSpec.Condition.AUTO
        ),
        spell_correction_spec=discoveryengine.SearchRequest.SpellCorrectionSpec(
            mode=discoveryengine.SearchRequest.SpellCorrectionSpec.Mode.AUTO
        ),
    )
    response = client.search(request=request)
    return [result.chunk.content for result in response if result.chunk and result.chunk.content]


def datastore_search_tool(search_query: str) -> list[str] | str:
    """Search boutique documents for store hours, location, history, and staff.

    Args:
        search_query: A question about Betty's Bird Boutique.

    Returns:
        Matching document text, or a safe status message when no result is available.
    """
    try:
        if not search_query or not search_query.strip():
            return "Please provide a store-related question to search for."
        results = search(
            project_id=os.environ.get("DATASTORE_PROJECT_ID", ""),
            location=os.environ.get("DATASTORE_LOCATION", "global"),
            engine_id=os.environ.get("DATASTORE_ENGINE_ID", ""),
            search_query=search_query,
        )
        return results if results else "No results found."
    except Exception as exc:
        # Do not return request details or exception text to the model or customer.
        logger.warning("Vertex AI Search failed (%s).", type(exc).__name__)
        return "Store information search is temporarily unavailable. Please try again later."
