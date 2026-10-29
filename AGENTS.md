# NetOne MCP — Agent Instructions

## Scope and current status

Read `PRD.md` before architectural/sprint work. PRD 1.7.0 / DEC-027 records Sprints 5, 6 and 7 complete. The maintainer explicitly accepted Sprint 7 with a documented exception: technical codigoSku has offline coverage but no real validation. S7.11 was revised to record this acceptance, not fabricated SKU proof or substitution by mascara. Real ID/EAN/commercial-code and text observations remain bounded; the current offline suite passes 116 tests. The registry remains empty until Sprint 9 and V1 is NOT_READY. All prior probe budgets are closed, including unused conditional allocations. No new ERP request, login, token rotation, environment-file modification, wider scan or Sprint 8+ is authorized. No private source value may be retained. Earlier open-S7.11 notes are historical under the original criterion; DEC-027 governs current acceptance.

## Boundaries

DEC-025 prioritizes application search_product_by_code for the operator's
commercial code/business SKU, using only the products mascara filter.
product_mask keyword-only string1–256, nonblank, no Unicode C; preserve
it exactly, reject combination with product_id or use in prices/stock.
Keep API codigoSku/sku and its function distinct; do not rename source
fields or infer model routing. Two authorized filtered requests succeeded,
confirming mascara and the public exact-code function; that probe is now
closed. No new ERP request or unrelated sprint checkbox change is authorized.

DEC-026 / PRD 1.6.0 adds evidence-based product-field presentation:
subgroup, notes, wholesale_price_table, wholesale_price and strict optional
boolean blocked. Existing functions share this immutable DTO. Filled
fields precede null/blank without dropping keys, missing metadata, exact
Decimal values, zero or false. Do not infer stock, sellability, currency,
final prices or discounts; no new price/stock consumer or Sprint 8 work.
The 100-row field profile used two page1/2 limit50 HTTP200 requests and
is closed. A separately approved one-row page1/limit1 metadata check also
finished with HTTP200 and completed cleanup; its budget is now closed.
Only names/types/presence states were retained for six extra fields.
Unit/packaging fields were filled in that one row; promotional fields
were null. Their names do not establish provider semantics, stock,
conversion, promotional pricing or coverage across the 100-row sample.
See docs/product-field-priority.md. Technical codigoSku remains unvalidated;
S7.11 is accepted with the explicit DEC-027 exception, not real SKU proof;
do not rerun probes or register MCP tools without separate authorization.

- `config.py` is the sole explicit loader/validator. Process variables override root dotenv without interpolation/environment mutation; imports perform no configuration I/O. Settings are immutable, token SecretStr, URL/token excluded from repr; never serialize settings.
- `server.py` is thin stdio/registry/lifespan. One private HTTPX client per lifespan; no startup request. Sprint 6 adds a callable `tools.search_products(client, query, max_results=20)` without registration; it validates input and matches local normalized text, never sends an undocumented text filter.
- `client.py` owns token auth, fixed-origin three-POST allowlist, closed page/limit filters, bounded streaming/pagination/errors. Products additionally accepts either strict product_id (idsProdutos singleton) or validated product_mask (mascara), never both, never arbitrary filters or changes to prices/stock. Per-call filters/budgets cannot mutate shared state. Validate ID-filtered response identity atomically; mask equality is enforced by the application without inventing provider semantics. `_query()` validates body; request hook checks method/origin/Host/route only. Never remove/bypass the guard for a probe.
- `catalog.py` owns immutable normalization consumed by private collection. Decimal serializes exactly as strings; preserve IDs/leading zeros, text and absent/null/zero. Timestamp stays raw. Duplicates/conflicts and missing metadata must not create false completeness.
- No arbitrary HTTP/SQL/commands, MCP configuration/tenant selection, commercial mutation, persistent cache/DB/UI/Docker/CI or autonomous agent. Analysis frameworks are optional only with a real justified consumer, not scaffolding.

## Security and lifecycle

Preserve `.env` exactly: no display/read/write/move during this refactor. Examples use empty credentials and neutral hosts. Only operator-approved HTTPS configuration, including private/single-label hosts, with fixed origin and verified certificates. No inherited proxy/netrc/CA override, redirects, retries or method/route fallback; legacy retry configuration is inert. No real ERP, login or token regeneration without separate explicit authorization.

Request `identity`, reject compressed success responses, limit raw body to 1 MiB and bound whole-query time/pages/rows. Use public build_request/send(stream=True) and response.stream protocol; no HTTPX state writes. Response and client closure are shielded with one-second bounds. Completed cleanup needs evidence, not merely closed state; a timeout is bounded failure, not release assurance.

stdout is MCP-only. Relevant/root log handlers emit safe level/component/code, never raw SDK/HTTP message/args/exception/stack. Do not indiscriminately disable loggers. Fixed safe application errors may remain specific. Never log settings, environment, headers, bodies or credentials.

## Development and verification

Use Python >=3.14,<4, one root `.venv`, one `requirements.txt`; preserve remaining direct pins and avoid unnecessary installs. LangChain/LangGraph are removed while unused; no LLM key required. English public docs/code/comments/logs; pt-BR PRD/plans; PEP 8, single quotes and Mermaid.

Offline unittest and mocked integration are allowed. Run `.venv/Scripts/python.exe -B -m unittest discover -s tests -v` and relevant safe checks; use only synthetic settings/streams, forbid HTTP sends and real `.env` access. Exercise stdio without LLM. Record actual relevant command/result/limits, not invented success. Update only documentation affected by meaningful decisions; no dossier per microchange. Mark checkboxes only with evidence and never change unrelated sprint states.

PRD policy permits read-only Git inspection, but commits/push/reset/branch changes require authorization; never edit `.git`. This delegated refactor explicitly performs no Git commands. Protected-tool timeout/refusal is a stop, not permission to use another write path. Do not modify another Hermes profile or out-of-scope files.
