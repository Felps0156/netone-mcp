"""Normalize documented query fields without inferring commercial facts."""

from dataclasses import asdict, dataclass
from decimal import Decimal
from typing import Literal


class NormalizationError(Exception):
    """Reject invalid commercial types without retaining source values."""

    def __init__(self) -> None:
        super().__init__('NetOne returned invalid commercial data.')


_TEXT_FIELDS = {
    'product_mask': 'mascara',
    'sku': 'codigoSku',
    'ean': 'ean',
    'description': 'descricao',
    'group': 'grupoDescricao',
    'line': 'linhaDescricao',
    'price_table': 'tabelaPreco',
    'last_changed_raw': 'ultimaAlteracaoTimestamp',
}
_DECIMAL_FIELDS = {
    'price': 'valor',
    'quantity': 'quantidade',
}


def _identifier(value: object, required: bool) -> str | None:
    if value is None and not required:
        return None
    if type(value) is int and value >= 0:
        return str(value)
    if (
        isinstance(value, str) and 1 <= len(value) <= 256
        and value.strip() and not any(ord(c) < 32 for c in value)
    ):
        return value
    raise NormalizationError()


def _text(value: object) -> str | None:
    if value is None or isinstance(value, str):
        return value
    raise NormalizationError()


def _decimal(value: object) -> Decimal | None:
    if value is None:
        return None
    if type(value) is int:
        return Decimal(value)
    if isinstance(value, Decimal) and value.is_finite():
        return value
    # A float has already lost source precision; never repair it by casting.
    raise NormalizationError()


@dataclass(frozen=True, slots=True)
class CatalogRecord:
    """An explicit projection, not a complete copy of an ERP product."""

    product_id: str | None
    reduced_id: str
    product_mask: str | None = None
    sku: str | None = None
    ean: str | None = None
    description: str | None = None
    group: str | None = None
    line: str | None = None
    price_table: str | None = None
    last_changed_raw: str | None = None
    price: Decimal | None = None
    quantity: Decimal | None = None
    missing_fields: tuple[str, ...] = ()

    def as_json(self) -> dict[str, object]:
        data = asdict(self)
        for key, value in data.items():
            if isinstance(value, Decimal):
                data[key] = str(value)
            elif isinstance(value, tuple):
                data[key] = list(value)
        return data


def normalize_record(operation: str, raw: object) -> CatalogRecord:
    """Preserve codes and text exactly; never derive scope or timestamps."""
    if operation not in ('products', 'prices', 'stock'):
        raise NormalizationError()
    if not isinstance(raw, dict):
        raise NormalizationError()
    product_id = _identifier(raw.get('idProduto'), operation != 'stock')
    reduced_id = _identifier(raw.get('idReduzido'), True)
    if reduced_id is None:
        raise NormalizationError()
    texts = {key: _text(raw.get(source))
             for key, source in _TEXT_FIELDS.items()}
    decimals = {key: _decimal(raw.get(source))
                for key, source in _DECIMAL_FIELDS.items()}
    sources = ('idProduto', 'idReduzido', *_TEXT_FIELDS.values(),
               *_DECIMAL_FIELDS.values())
    return CatalogRecord(
        product_id=product_id, reduced_id=reduced_id,
        product_mask=texts['product_mask'], sku=texts['sku'],
        ean=texts['ean'], description=texts['description'],
        group=texts['group'], line=texts['line'],
        price_table=texts['price_table'],
        last_changed_raw=texts['last_changed_raw'],
        price=decimals['price'],
        quantity=decimals['quantity'],
        missing_fields=tuple(key for key in sources if key not in raw),
    )


@dataclass(frozen=True, slots=True)
class QueryResult:
    """Report only a bounded endpoint traversal, never a global snapshot."""

    status: Literal['found', 'not_found', 'partial', 'error']
    items: tuple[CatalogRecord, ...] = ()
    partial: bool = False
    warnings: tuple[str, ...] = ()
    error: str | None = None
    source: Literal['netone_api'] = 'netone_api'
    retrieved_at: str | None = None
    operation: str = ''
    pages_fetched: int = 0
    rows_received: int = 0
    total_pages: int | None = None
    total_elements: int | None = None
    complete_dataset: bool = False

    def as_json(self) -> dict[str, object]:
        data = asdict(self)
        data['items'] = [item.as_json() for item in self.items]
        data['warnings'] = list(self.warnings)
        data['returned_count'] = len(self.items)
        return data
