# NetOne MCP — Agent Instructions

## Scope and current status

PRD 1.9.1 / DEC-031 records Sprint 9 complete. The maintainer authorized
one list_products call through a generic MCP stdio client, page1/limit1,
with existing configuration loaded only in memory through load_config.
The one-shot completed at2026-10-30T01:47:59Z: one attempt HTTP200, one
received/returned item, partial=true, error=null, complete_dataset=false.
Same-response projection/Decimal/null/absence and JSON equivalence passed;
response, transport and client cleanup completed. S9.12 marked complete,
G3 PASS only in this bounded scope; V1 NOT_READY. Budget consumed and
closed: no rerun, extra ERP/configuration access, login/rotation, .env
modification, mutation, Git or Sprint10. Retain only structural evidence.

The maintainer subsequently approved Sprint 9's incremental offline MCP
integration and the narrow revision of the earlier no-registration rule.
The approved scope is recorded in docs/superpowers/specs/2026-10-29-sprint-9-design.md
and docs/superpowers/plans/2026-10-29-sprint-9.md. This supersedes only the
no-Sprint9/empty-registry statements below: expose the seven evidenced
application capabilities, excluding technical SKU and expanded search.
No further real .env access, ERP query, login, token rotation, Git, new
HTTP filter, Sprint10 or V1 release is authorized. Earlier budgets remain
closed. Synthetic integration remains distinct from the real one-shot above.

Read PRD.md before architectural/sprint work. DEC-030 records
Sprint 9 offline discovery/execution of exactly search_products,
search_product_by_code, get_product_details, search_product_by_ean,
get_product_price, check_inventory and list_products. DEC-031 adds S9.12's
real listing proof, not real MCP coverage of every tool. Sprints 5–8 remain accepted within
their own bounded evidence; DEC-027 is not real technical-SKU proof.
No private source value may be retained. Application HTTP/filter/config/
normalization behavior is unchanged; MCP price currency remains unknown.

## Historical Sprint 8 scope — completed and budget closed

The maintainer subsequently approved the Sprint 8 design and execution plan
in docs/superpowers/specs/2026-10-29-sprint-8-design.md and
docs/superpowers/plans/2026-10-29-sprint-8.md. This supersedes only the
earlier prohibition on starting Sprint 8 or its price/stock consumers.
Implement local exact identity selection on the existing page/limit-only
prices/stock queries and bounded product listing, one page by default.
No new HTTP filters, routes, MCP tools or Sprint 9 work are authorized.
BRL is operator-confirmed installation context, not an API-returned field.
After offline tests, independent review and verified probe fixes, the
one-shot validation read configuration in memory through the existing
loader and consumed five page1/limit1 queries: prices discovery + public
price function, stock discovery + public inventory function, and public
listing. Two prices, two stock, one products send; all HTTP200, each public
function one matching item/partial/error null, same-response fidelity/JSON
accepted and all response/client cleanup completed. Budget closed: no rerun.
Persist only approved structural counts/invariants, never source values.
No ERP mutation, login, token rotation, .env modification or Git commands.
All earlier probe budgets remain closed. Mark only evidenced S8 tasks.

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
final prices or discounts. DEC-026 itself did not authorize Sprint 8;
the later DEC-029 consumers are governed by the completed scope above.
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
- `server.py` is thin stdio/lifespan, one private client per lifespan and no startup request. `mcp_tools.py` specializes public FastMCP list_tools/call_tool hooks with an explicit seven-tool registry, strict extra-forbid models and fixed safe errors. No SDK edits or generic model-controlled dispatch outside the registry. `tools.py` remains the application layer; local search never sends an undocumented text filter. Cancellation must propagate and cleanup completion must be observed.
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
