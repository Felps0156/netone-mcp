# Product-field availability and presentation priority

## Evidence and limits

PRD 1.6.0 / DEC-026. On 2026-10-29 at 18:52:18 UTC, an explicitly
approved sample inspected 100 received product rows: two guarded POST
requests to produto/reduzidos, page1/page2, limit50, both HTTP200.
The existing loader/token, verified TLS, fixed-origin/route guard and
bounded response reader were used. No login, retries, redirects, token
rotation, environment-file change, price/stock request or source-value
persistence occurred. Client cleanup completed. The observation is closed.

This is a catalog prefix, not a random or representative sample, global
snapshot, supplier schema guarantee or stock/price quote. The provider's
terminal page was not reached. Counts are per received row, not deduplicated
product identity; reduced variants can belong to the same product.

39 predefined documented/projected names were checked: 36 were present
in at least one row; 30 had at least one filled value and 28 were filled
in all 100 rows. Six additional source keys existed outside the whitelist;
only that count was retained, not their names, values or shapes. Those
original names cannot be reconstructed or their frequencies inferred.
The later separately approved one-row check below identifies six extras
in its own response, not retrospectively across all 100 rows. Neither
observation establishes every possible field in the provider's catalog.

## Approved one-row extra-field metadata follow-up

With separate explicit operator authorization, one additional products
request started on 2026-10-29 at 20:56:08 UTC, page1/limit1. The operator
also renewed the protected AGENTS.md documentation update. The request
returned HTTP200 and one row.
The current five-field projection accepted the row; response/client
cleanup completed. Only the following names/types/presence states were
retained. No names were withheld by the structural-name safety check.

| Extra source field | Observed type | State in this one row |
|---|---|---|
| descricaoPromocao | null | null |
| descricaoPromocaoAtacado | null | null |
| quantidadePecasPorEmbalagem | integer | filled |
| unidadeDeMedidaSigla | string | filled |
| valorPromocional | null | null |
| valorPromocionalAtacado | null | null |

The six-key count agrees with the earlier count, but discarded original
names cannot prove set identity across observations. The null fields'
non-null types and promotion semantics remain unknown. Filled unit and
packaging metadata are useful context candidates, not stock, availability,
a conversion formula or a new filter. They are not added to the current
DTO by this metadata-only authorization. Preserve their distinct source
names; do not substitute them for quantidade or treat promotional fields
as an accepted price. No values, units, quantities or prices were stored.
This single-request budget is now exhausted; no automatic repeat or
additional technical-SKU discovery is authorized.

## Definitions

- Filled: non-null, nonblank string or a nonempty container, or a scalar.
- Null: key present with JSON null; different from absent.
- Blank: empty/whitespace-only string, without rewriting its source value.
- Empty: an empty array/object; different from null or absent.
- Zero/false: subsets of filled, not empty. Their counts are not additive.
- Presence does not prove meaningful color/size, correct dimensions,
  sellable status, stock, a final price, currency or discount application.

Only field names, type labels and aggregate counts are recorded below.
No identifiers, descriptions, notes, amounts, URLs, origins or credentials
from the ERP are retained.

## Entire 100-row checked-name inventory

Each row's Filled + Null + Blank + Empty + Absent equals 100.

| Source field | Filled | Null | Blank | Empty | Absent | Zero | False | Observed types |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| idProduto | 100 | 0 | 0 | 0 | 0 | 0 | 0 | integer |
| idReduzido | 100 | 0 | 0 | 0 | 0 | 0 | 0 | integer |
| mascara | 100 | 0 | 0 | 0 | 0 | 0 | 0 | string |
| descricao | 100 | 0 | 0 | 0 | 0 | 0 | 0 | string |
| codigoSku | 0 | 100 | 0 | 0 | 0 | 0 | 0 | null |
| ean | 93 | 7 | 0 | 0 | 0 | 0 | 0 | string/null |
| grupoDescricao | 100 | 0 | 0 | 0 | 0 | 0 | 0 | string |
| subgrupoDescricao | 100 | 0 | 0 | 0 | 0 | 0 | 0 | string |
| modeloDescricao | 0 | 0 | 100 | 0 | 0 | 0 | 0 | string |
| linhaDescricao | 100 | 0 | 0 | 0 | 0 | 0 | 0 | string |
| colecao | 0 | 0 | 100 | 0 | 0 | 0 | 0 | string |
| corCodigo | 100 | 0 | 0 | 0 | 0 | 100 | 0 | integer |
| corDescricao | 100 | 0 | 0 | 0 | 0 | 0 | 0 | string |
| cor | 100 | 0 | 0 | 0 | 0 | 0 | 0 | string |
| tamanhoSigla | 100 | 0 | 0 | 0 | 0 | 0 | 0 | string |
| tamanhoOrdem | 100 | 0 | 0 | 0 | 0 | 0 | 0 | integer |
| tamanho | 100 | 0 | 0 | 0 | 0 | 0 | 0 | string |
| gradeNumero | 100 | 0 | 0 | 0 | 0 | 100 | 0 | integer |
| imagens | 0 | 0 | 0 | 100 | 0 | 0 | 0 | array |
| urlImagens | 0 | 0 | 0 | 100 | 0 | 0 | 0 | array |
| pesoBruto | 100 | 0 | 0 | 0 | 0 | 100 | 0 | integer |
| pesoLiquido | 100 | 0 | 0 | 0 | 0 | 100 | 0 | integer |
| largura | 100 | 0 | 0 | 0 | 0 | 100 | 0 | integer |
| comprimento | 100 | 0 | 0 | 0 | 0 | 100 | 0 | integer |
| altura | 100 | 0 | 0 | 0 | 0 | 100 | 0 | integer |
| observacao | 1 | 0 | 99 | 0 | 0 | 0 | 0 | string |
| observacaoDetalhes | 0 | 0 | 100 | 0 | 0 | 0 | 0 | string |
| tabelaPreco | 100 | 0 | 0 | 0 | 0 | 0 | 0 | string |
| valor | 100 | 0 | 0 | 0 | 0 | 0 | 0 | decimal |
| percentualDesconto | 100 | 0 | 0 | 0 | 0 | 100 | 0 | integer |
| tabelaPrecoAtacado | 100 | 0 | 0 | 0 | 0 | 0 | 0 | string |
| valorAtacado | 100 | 0 | 0 | 0 | 0 | 0 | 0 | decimal |
| percentualDescontoAtacado | 100 | 0 | 0 | 0 | 0 | 100 | 0 | integer |
| medidasEditaveisNoPedido | 100 | 0 | 0 | 0 | 0 | 0 | 100 | boolean |
| bloqueado | 100 | 0 | 0 | 0 | 0 | 0 | 100 | boolean |
| classificacoesItensIds | 0 | 0 | 0 | 0 | 100 | 0 | 0 | not observed |
| categoriasIds | 0 | 0 | 0 | 0 | 100 | 0 | 0 | not observed |
| ultimaAlteracaoTimestamp | 100 | 0 | 0 | 0 | 0 | 0 | 0 | string |
| quantidade | 0 | 0 | 0 | 0 | 100 | 0 | 0 | not observed |

## Applied priority and explicit scope decisions

P0 identity for the operator: mascara/product_mask and descricao/description.
Never substitute codigoSku, EAN or an internal ID for the commercial code.

P1 context and source status: bloqueado/blocked; grupoDescricao/group,
subgrupoDescricao/subgroup, linhaDescricao/line; ean; preserved product_id
and reduced_id. Source blocked is a strict optional boolean, not a locally
invented availability result. False is not missing; true does not discard
a product or turn the query into not_found. Neither value proves stock or
permission to sell. EAN remains optional, exact text, leading zeros intact.

P2 product-source commercial data: valor/price, tabelaPreco/price_table,
valorAtacado/wholesale_price, tabelaPrecoAtacado/wholesale_price_table.
These were already present in the products response; there is no new
price-endpoint consumer, query, join or Sprint8 implementation. Decimals
remain exact strings with their original scale. Do not infer currency,
operator table selection, discounts/taxes or final sale price. Discount
percentages are inventoried but not applied or added to this DTO.

P3 optional notes and provenance: observacao/notes only when populated;
ultimaAlteracaoTimestamp/last_changed_raw remains opaque. Notes are source
data, never instructions, logs or code. SKU stays separate and available
when legitimately filled. Quantity is unknown here, not zero; no stock
claim is possible from this endpoint sample.

Deferred, not erased from the source: color/size text is populated but its
business significance was not assessed. Do not equate zero color/grade or
zero measurements with missing, or assume zero dimensions are usable for
shipping. Empty images, model/collection/detail-notes and absent category/
classification arrays do not become priority search requirements. None of
these fields needs a new parser/filter/framework without a real consumer.
For the later one-row extra-field evidence above, unit/packaging are
secondary context candidates; null promotional fields have no current
presentation priority. Both remain outside the implemented five-field
extension, with no invented type/price/conversion semantics.

## Application output contract

All existing application functions consume the same immutable CatalogRecord
projection, now adding five optional fields: subgroup, notes,
wholesale_price_table, wholesale_price and blocked. New fields are typed;
invalid values fail with a fixed sanitized error. An absent projected source
key is listed in missing_fields; explicit null is not. Text is not trimmed,
casefolded or coerced. Adding optional projections expands output keys and
missing_fields; clients must read names rather than fixed object lengths.

CatalogRecord.as_json emits populated fields first, in the priorities above,
then null/blank fields, and missing_fields last. False and zero are populated.
No old key or blank/null value is removed. This is deterministic JSON
presentation only: consumers must not depend on object-key order. It does
not implement an LLM router, change matching, or rank search results. Query
error/partiality/completeness metadata remains unchanged.

The 100 null codigoSku values cannot validate a real exact-SKU match.
Later PRD 1.7.0 / DEC-027 closes Sprint 7 through explicit maintainer
acceptance with this exception and a revised S7.11 criterion, not new
technical-SKU evidence. No other sprint task changes; V1 remains NOT_READY,
the MCP registry is empty and Sprint 8 has not started.
