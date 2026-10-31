# NetOne MCP — Agent Instructions

## Scope and current status

Sprint13 execution checkpoint: clean-install195 PASS on Windows/Python3.14.3,
temporary environment removed/root .venv retained. Separately authorized one
private loader read and one real MCP listing completed2026-10-31T16:04:21Z:
one POST reduced-products page1/limit1, HTTP200, one partial item, exact
same-response fidelity/JSON and response/transport/client cleanup accepted.
Read/query budget CONSUMED/CLOSED: no rerun or new .env/ERP access. All source,
tests and pins unchanged. S13.01–20 evidenced, matrix20 rows, independent
review195 PASS/8.254s and12 harness PASS/6.208s, no Critical/Important.
Historical checkpoint wording was reconciled during final status closure.
No final sprint acceptance is declared while G6/global criteria are pending.
G6/global acceptance stays pending, V1 NOT_READY. No Git/publication.
The authorization history immediately below explains the phases, not new
permission to repeat the consumed installation/private/query actions.

Sprint13: the maintainer approved the design (including the VM11 correction)
and native execution plan, docs/superpowers/specs/2026-10-31-sprint-13-design.md
and docs/superpowers/plans/2026-10-31-sprint-13.md. PRD1.13.0/DEC-036 admits
offline validation, public documentation and temporary synthetic probes in
managed scratch, followed by independent final review. This supersedes only
the earlier exclusion of13 for this approved slice. No production/test/pin
change is planned. Mark only independently evidenced S13 items; preserve all
other sprint/global checkboxes. Installation/temporary-environment exception,
private load_config read and one real MCP listing each need specific consent;
none is authorized by plan approval. Earlier ERP budgets remain exhausted.
The maintainer later approved all three separate consent questions: clean
temporary environment/install/tests/removal in managed scratch (root .venv
untouched), one private load_config invocation in the server's memory, and
one list_products MCP attempt POST reduzidos/page1/limit1. No extra discovery,
retry/redirect, login/rotation or .env write; retain only safe counts/codes/
test times/fidelity/JSON/cleanup booleans. Record consumption in the runbook;
these are new nonrenewable permissions, not reopened historical budgets.
No real .env read/write, ERP, Git, installs, login/rotation, new tool/filter
or publication until the applicable explicit permission. Seven MCP tools,
bounded G3/G4, G6 pending and V1 NOT_READY remain. Evidence: docs/runbook.md,
Sprint13. VM11 separates a valid empty result from an HTTP404 endpoint error;
do not change production to turn404 into successful absence.

Historical Sprints12/14 checkpoint (superseded only as described above):
The maintainer approved only Sprints12 and14, their design and execution
through final verification without intermediate approval gates. Sprint13
remains outside scope and its checklist must remain unchanged. Design/plan:
docs/superpowers/specs/2026-10-31-sprints-12-14-design.md and
docs/superpowers/plans/2026-10-31-sprints-12-14.md. PRD1.12.0/DEC-035 governs
public-documentation consolidation and controlled technical handoff, not
publication or V1 release. Earlier no-Sprint12+ statements below describe
their historical checkpoints and are superseded only for this approved slice.
No real .env access/write, ERP, login/rotation, Git, installs, new filters/
tools or production/test changes. Seven MCP tools, bounded G3/G4 and
V1 NOT_READY remain. New guides: docs/architecture.md, docs/security.md,
docs/local-dev.md, docs/attributions.md. Project license choice and separate
Git/index/history publication audit remain owner actions; no legal or
operational clearance follows from documentation. Current evidence and
per-task acceptance belong in docs/runbook.md, Sprints12/14.
S12.01–14 and S14.01–14 are complete in that documentation-only scope.
Final coordinator regression:195 PASS/8.947s; independent review:195
PASS/8.959s; pip check PASS. Audit:61 public files/103 local links and
anchors/226 ordered tasks, exactly28 approved state changes; Sprint13
stays0/20 and global checkboxes unchanged. No Critical/Important findings;
two final documentation/status reconciliation items were resolved. G5 is
limited to public documentation, G6 pending; project licensing and release
criteria remain open. Existing source line-length debt is unchanged.
After the public audit, the maintainer explicitly authorized narrowly scoped
privacy substitutions in the two historical archives and Sprint5/9/11 plans.
Only identifying business/local-path references may change; preserve all
decisions/results/task wording/order/states. The archive index records the
redaction instead of claiming verbatim equality. No private-file/Git access.

Sprint11 / PRD1.11.0 DEC-034 is complete in its offline security/quality
scope. The maintainer chose option1 (review and minimal verified fixes)
and direct native execution without intermediate approval gates.
Plan: docs/superpowers/plans/2026-10-30-sprint-11.md; evidence and residual
limits: docs/runbook.md, Sprint11. S11.01–13 are marked with evidence.
Coordinator:195 tests PASS/8.643s; independent review:195 PASS/8.629s;
pip check PASS, no Critical/Important findings. Existing long lines remain
documented Minor style debt. No new operational evidence was obtained.
This supersedes earlier no-Sprint11 checkpoints below, not their closed
ERP budgets. No real .env access/write, ERP, login/rotation, Git, installs,
new filters/tools, Sprint12+ or V1 release is authorized. Registry stays
exactly seven tools; G3/G4 retain their bounded scope and V1 is NOT_READY.
Application ToolInputError (ValueError subtype) identifies registered-tool
input failures; internal ValueError/serialization errors use safe tool_error.
Listing page_size validates against the effective row cap before collection;
invalid input now raises ToolInputError, not collector BlockedOperationError.
Application-only lexical/analysis validators retain their existing behavior.
S11.06 covers no protected-file access/mutation during this execution,
not historical checksum equality or a third-party-change guarantee.

Sprint10 / PRD1.10.0 DEC-033: maintainer chose application-only option1,
approved docs/superpowers/specs/2026-10-30-sprint-10-design.md with low-stock
default3, then the native execution plan. Implemented tools.analyze_inventory
and tools.analyze_product_catalog with typed pure aggregation in analysis.py;
independent final review found no Critical/Important/Minor issues.
S10.01–15 are complete in their offline scope. Threshold is configurable per call,
known quantity <=3 by default, never an ERP-derived rule. Exact reduced
identities count once; conflicting groups are excluded from metrics while
source records remain. Null/absent quantities stay unknown. No unit/deposit
sums, LLM/framework, join, new HTTP filters/dependencies or MCP tools.
Default max_results100/max_pages1 remains capped by existing configuration;
collection completeness, analytical completeness and metric sufficiency are
distinct. All new verification uses synthetic settings/transports, with
190 tests PASS and pip check PASS, independently rerun during review. G4
passes only for bounded synthetic analyses, not operational evidence. This later
approval supersedes only earlier no-Sprint10 statements below (historical
scope checkpoints). All real .env/ERP budgets remain closed, no login/
rotation, Git, Sprint11+ or V1 release; registry stays exactly seven tools.

Sprint 9.5 is complete in its offline scope (PRD1.9.3 / DEC-032):170 tests
passed after review and a normalization-empty Unicode regression fix;
pip check passed. No new real evidence or budget was obtained.
The maintainer subsequently authorized Sprint 9.5 offline execution and
approved docs/superpowers/specs/2026-10-29-sprint-9-5-design.md and its plan.
PRD DEC-032 governs local search/serialization changes: max_results still
counts received rows, default100 only for literal/expanded searches, with
independent max_items20. Existing explicit row budgets/configured caps remain.
QueryResult exposes effective budgets; search separates collection completeness
from output cuts. Expanded lexical matching/composition stays application-only;
MCP still exposes exactly seven tools, with literal search and no lexical mode.
Price/stock filters remain planning-only; stock number/array conflict persists.
No real .env access, ERP query, login/rotation, Git, new HTTP filter, dependency,
tool or Sprint10 is authorized. Prior real evidence/budgets below are unchanged.

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
