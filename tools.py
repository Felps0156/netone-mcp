"""Bounded local product search; no MCP registration is approved here."""

from dataclasses import replace
import re
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


# Related names are possible alternatives, not proof of product equivalence.
_REVIEWED_RELATED_TERMS = {
    'manopla': ('punho',),
    'punho': ('manopla',),
}


def _search_term(value: object) -> str:
    if (
        not isinstance(value, str) or not 1 <= len(value) <= 200
        or not value.strip()
        or any(unicodedata.category(char).startswith('C') for char in value)
    ):
        raise ValueError('Search terms must be 1 to 200 characters without controls.')
    return value.strip()


def _search_terms(values: object) -> tuple[str, ...]:
    if not isinstance(values, (tuple, list)) or len(values) > 20:
        raise ValueError('Search terms must be a list of at most 20 strings.')
    return tuple(_search_term(value) for value in values)


async def search_products_expanded(
    client: NetOneClient, query: str, *,
    required_terms: tuple[str, ...] = (),
    suggested_terms: tuple[str, ...] = (),
) -> dict[str, object]:
    """Search a product term and separate textual restrictions, locally.

    Related terms are possible matches, not proof of equivalence. A complete
    traversal is neither a snapshot nor proof of semantic coverage.
    """
    original = _search_term(query)
    required = _search_terms(required_terms)
    suggested = _search_terms(suggested_terms)
    reviewed = _REVIEWED_RELATED_TERMS.get(original.casefold(), ())
    terms: list[tuple[str, str]] = []
    seen: set[str] = set()
    for kind, candidates in (
        ('direct', (original,)), ('reviewed', reviewed),
        ('suggested', suggested),
    ):
        for candidate in candidates:
            key = candidate.casefold()
            if key not in seen:
                seen.add(key)
                terms.append((candidate, kind))
    result = await client._collect('products')
    if 'duplicate_rows_removed' in result.warnings:
        result = replace(result, status='partial', partial=True,
                         complete_dataset=False)
    items: list[CatalogRecord] = []
    matches: list[dict[str, object]] = []
    unverified = 0
    for item in result.items:
        description = (item.description or '').casefold()
        matched = [(term, kind) for term, kind in terms
                   if term.casefold() in description]
        if matched and any(
            re.search(r'(?<!\w)' + re.escape(term.casefold()) + r'(?!\w)',
                      description) is None for term in required
        ):
            unverified += 1
            continue
        if matched:
            items.append(item)
            matches.append({
                'matched_terms': [term for term, _ in matched],
                'match_type': matched[0][1],
            })
    output = _filtered_result(result, tuple(items), 'local_related_text_search')
    output['matches'] = matches
    output['search_terms'] = [
        {'term': term, 'type': kind} for term, kind in terms
    ]
    output['required_terms'] = list(required)
    output['unverified_restriction_count'] = unverified
    output['warnings'] = [
        *result.warnings, 'local_related_text_search',
        'traversal_not_snapshot_or_semantic_coverage',
    ]
    return output


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
