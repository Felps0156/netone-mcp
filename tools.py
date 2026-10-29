"""Bounded local product search; no MCP registration is approved here."""

from dataclasses import replace
import unicodedata

from client import NetOneClient


async def search_products(
    client: NetOneClient, query: str, max_results: int = 20,
) -> dict[str, object]:
    """Filter a bounded product traversal, not a remote text-search result.

    The row budget includes nonmatches and duplicates and is capped by the
    client configuration. Partial collection remains partial even when no
    text matches. Source values and collection metadata stay unchanged.
    """
    if (
        not isinstance(query, str) or not 1 <= len(query) <= 200
        or not query.strip()
        or any(unicodedata.category(char).startswith('C') for char in query)
    ):
        raise ValueError('Query must be 1 to 200 characters without controls.')
    if type(max_results) is not int or not 1 <= max_results <= 1000:
        raise ValueError('max_results must be an integer from 1 to 1000.')

    needle = query.strip().casefold()
    result = await client._collect('products', max_results=max_results)
    items = tuple(
        item for item in result.items
        if any(
            value is not None and needle in value.casefold()
            for value in (item.description, item.product_mask, item.sku)
        )
    )
    status = result.status
    if status not in ('partial', 'error'):
        status = 'found' if items else 'not_found'
    return replace(
        result, items=items, status=status,
        warnings=(*result.warnings, 'local_text_search'),
    ).as_json()
