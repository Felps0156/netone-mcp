"""Aggregate bounded normalized records without inferring commercial facts."""

from dataclasses import dataclass
from decimal import Decimal
from typing import Literal

from catalog import CatalogRecord, QueryResult


@dataclass(frozen=True, slots=True)
class AnalysisUniverse:
    """Keep one unambiguous record per exact reduced identity."""

    records: tuple[CatalogRecord, ...]
    distinct_reduced_ids: int
    conflicting_identity_count: int
    duplicate_records_excluded: int


def prepare_universe(items: tuple[CatalogRecord, ...]) -> AnalysisUniverse:
    groups: dict[str, set[CatalogRecord]] = {}
    duplicates = 0
    for record in items:
        group = groups.setdefault(record.reduced_id, set())
        if record in group:
            duplicates += 1
        group.add(record)
    return AnalysisUniverse(
        records=tuple(next(iter(group)) for group in groups.values()
                      if len(group) == 1),
        distinct_reduced_ids=len(groups),
        conflicting_identity_count=sum(len(group) > 1
                                       for group in groups.values()),
        duplicate_records_excluded=duplicates,
    )


def validate_threshold(value: object) -> Decimal:
    """Reject coercion and costly representations before collection."""
    message = 'Threshold must be a bounded finite nonnegative decimal.'
    if type(value) is int:
        # Bound before converting, even when Python's int string cap is lower.
        if not 0 <= value < 10 ** 100:
            raise ValueError(message)
        amount = Decimal(value)
    elif isinstance(value, Decimal):
        amount = value
    else:
        raise ValueError(message)
    if not amount.is_finite() or amount < 0:
        raise ValueError(message)
    parts = amount.as_tuple()
    if (len(parts.digits) > 100 or not isinstance(parts.exponent, int)
            or not -100 <= parts.exponent <= 100):
        raise ValueError(message)
    return amount


def inventory_metrics(
    universe: AnalysisUniverse, threshold: Decimal,
) -> dict[str, object]:
    known = [record.quantity for record in universe.records
             if record.quantity is not None]
    absent = sum('quantidade' in record.missing_fields
                 for record in universe.records if record.quantity is None)
    unknown = len(universe.records) - len(known)
    return {
        'known_quantity_count': len(known),
        'unknown_quantity_count': unknown,
        'null_quantity_count': unknown - absent,
        'absent_quantity_count': absent,
        'low_stock_count': sum(value <= threshold for value in known),
        'zero_quantity_count': sum(value == 0 for value in known),
        'negative_quantity_count': sum(value < 0 for value in known),
        'above_threshold_count': sum(value > threshold for value in known),
    }


def _presence(record: CatalogRecord, field: str, source: str) -> str:
    if source in record.missing_fields:
        return 'absent'
    value = getattr(record, field)
    if value is None:
        return 'null'
    if isinstance(value, str) and not value.strip():
        return 'blank'
    return 'populated'


def catalog_metrics(universe: AnalysisUniverse) -> dict[str, object]:
    presence = {}
    for field, source in (
        ('product_mask', 'mascara'), ('description', 'descricao'),
        ('sku', 'codigoSku'), ('ean', 'ean'),
    ):
        counts: dict[str, int] = dict.fromkeys(
            ('populated', 'absent', 'null', 'blank'), 0,
        )
        for record in universe.records:
            counts[_presence(record, field, source)] += 1
        presence[field] = counts
    classifications = {}
    for field, source in (
        ('group', 'grupoDescricao'), ('subgroup', 'subgrupoDescricao'),
        ('line', 'linhaDescricao'),
    ):
        values: dict[str, int] = {}
        missing: dict[str, int] = dict.fromkeys(('absent', 'null', 'blank'), 0)
        for record in universe.records:
            state = _presence(record, field, source)
            if state == 'populated':
                value = getattr(record, field)
                values[value] = values.get(value, 0) + 1
            else:
                missing[state] += 1
        classifications[field] = {
            'values': [{'value': value, 'count': count}
                       for value, count in values.items()], **missing,
        }
    absent = sum('bloqueado' in record.missing_fields
                 for record in universe.records)
    unknown = sum(record.blocked is None for record in universe.records)
    return {
        'distinct_product_count': len({record.product_id
                                       for record in universe.records
                                       if record.product_id is not None}),
        'field_presence': presence,
        'blocked_counts': {
            'true': sum(record.blocked is True for record in universe.records),
            'false': sum(record.blocked is False
                         for record in universe.records),
            'unknown': unknown, 'null': unknown - absent, 'absent': absent,
        },
        'classifications': classifications,
    }


def analysis_result(
    result: QueryResult, universe: AnalysisUniverse, *,
    analysis_type: Literal['inventory', 'product_catalog'],
    metrics: dict[str, object], threshold: Decimal | None = None,
) -> dict[str, object]:
    """Keep collection evidence separate from analytical admissibility."""
    uncertain = (
        universe.conflicting_identity_count > 0
        or universe.duplicate_records_excluded > 0
        or 'duplicate_rows_removed' in result.warnings
        or 'conflicting_rows_preserved' in result.warnings
    )
    complete = (
        result.complete_dataset and result.error is None and not uncertain
    )
    output = result.as_json()
    warnings = list(result.warnings)
    if not complete:
        warnings.append('analysis_universe_incomplete')
        if result.status != 'error':
            output['status'] = 'partial'
        output['partial'] = True
    warnings.append('traversal_not_snapshot_or_global_erp_coverage')
    criteria = {
        'counting_unit': 'exact reduced_id with one unambiguous record',
        'conflicts': 'exclude the entire identity group; retain source items',
        'duplicates': 'count identical projected records once',
        'denominator': 'records_analyzed; excludes conflicting identities',
        'completeness': 'visible endpoint traversal, not ERP-wide or snapshot',
    }
    metrics_complete = universe.conflicting_identity_count == 0
    if analysis_type == 'inventory':
        metrics_complete = (
            metrics_complete and metrics['unknown_quantity_count'] == 0
        )
        criteria.update(
            low_stock='known quantity <= threshold',
            unknown='null and absent quantities are not zero or classified',
            subsets='zero and negative counts overlap low_stock_count',
            aggregation='no quantity sums across units or deposits',
        )
        output['inventory_scope'] = {
            'selection': 'configured_user_deposit', 'deposit_id': None,
            'branch_id': None, 'quantity_basis': 'physical_minus_reservations',
        }
        warnings.extend(('inventory_scope_unverified',
                         'inventory_freshness_unverified'))
        if metrics['unknown_quantity_count']:
            warnings.append('quantity_missing')
    else:
        criteria.update(
            field_presence='absent, null, blank and populated are distinct',
            classifications='exact source text; missing states separate',
            blocked='source boolean, not proof of sellability',
        )
    output.update(
        analysis_type=analysis_type, records_analyzed=len(universe.records),
        source_record_count=len(result.items),
        distinct_reduced_ids=universe.distinct_reduced_ids,
        conflicting_identity_count=universe.conflicting_identity_count,
        duplicate_records_excluded=universe.duplicate_records_excluded,
        collection_complete=result.complete_dataset, complete_dataset=complete,
        metrics_complete=metrics_complete, criteria=criteria, metrics=metrics,
        threshold=str(threshold) if threshold is not None else None,
        analysis_scope='visible_endpoint' if complete else 'sample',
        warnings=warnings,
    )
    return output
