"""Bounded local product search; no MCP registration is approved here."""

from dataclasses import replace
from typing import Literal
import unicodedata

from client import NetOneClient
from catalog import CatalogRecord, QueryResult


def _filtered_result(
    result: QueryResult, items: tuple[CatalogRecord, ...], warning: str,
) -> dict[str, object]:
    """Retain collection failures and completeness when selecting records."""
    status = result.status
    if status not in ('partial', 'error'):
        status = 'found' if items else 'not_found'
    return replace(
        result, items=items, status=status,
        warnings=(*result.warnings, warning),
    ).as_json()


def _validate_code_input(code: object, max_results: object) -> None:
    """Validate without transforming source codes or echoing rejected data."""
    if (
        not isinstance(code, str) or not 1 <= len(code) <= 256
        or not code.strip()
        or any(unicodedata.category(char).startswith('C') for char in code)
    ):
        raise ValueError('Code must be 1 to 256 characters without controls.')
    if type(max_results) is not int or not 1 <= max_results <= 1000:
        raise ValueError('max_results must be an integer from 1 to 1000.')


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
    return _filtered_result(result, items, 'local_text_search')


async def get_product_details(
    client: NetOneClient, product_id: int, max_results: int = 20,
) -> dict[str, object]:
    """Return bounded reduced records for one strictly validated product ID."""
    if (
        type(product_id) is not int
        or not 0 <= product_id <= 9223372036854775807
    ):
        raise ValueError('product_id must be an integer from 0 to 2**63 - 1.')
    if type(max_results) is not int or not 1 <= max_results <= 1000:
        raise ValueError('max_results must be an integer from 1 to 1000.')
    result = await client._collect(
        'products', max_results=max_results, product_id=product_id,
    )
    return result.as_json()


async def _search_exact_code(
    client: NetOneClient, code: str, max_results: int,
    field: Literal['sku', 'ean'],
) -> dict[str, object]:
    """Compare one source field exactly within a bounded local traversal."""
    _validate_code_input(code, max_results)
    result = await client._collect('products', max_results=max_results)
    items = tuple(
        item for item in result.items if getattr(item, field) == code
    )
    return _filtered_result(result, items, f'local_exact_{field}_search')


async def search_product_by_code(
    client: NetOneClient, code: str, max_results: int = 20,
) -> dict[str, object]:
    """Prefer the commercial mask/code; keep API codigoSku separate.

    The provider's mask-filter equality is not assumed. Select exact masks
    locally from its bounded filtered response, preserving partial/errors.
    """
    _validate_code_input(code, max_results)
    result = await client._collect(
        'products', max_results=max_results, product_mask=code,
    )
    items = tuple(item for item in result.items if item.product_mask == code)
    return _filtered_result(result, items, 'remote_product_code_exact_match')


async def search_product_by_sku(
    client: NetOneClient, sku: str, max_results: int = 20,
) -> dict[str, object]:
    """Match codigoSku exactly; a bounded miss never proves global absence."""
    return await _search_exact_code(client, sku, max_results, 'sku')


async def search_product_by_ean(
    client: NetOneClient, ean: str, max_results: int = 20,
) -> dict[str, object]:
    """Match ean exactly without trimming, coercion or checksum inference."""
    return await _search_exact_code(client, ean, max_results, 'ean')
