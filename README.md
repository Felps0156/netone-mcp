# NetOne MCP

A Python MCP stdio server for authorized, bounded read-only NetOne ERP queries,
with deterministic catalog/inventory analyses available in the application layer.
It preserves exact source values and reports incomplete evidence rather than
inventing commercial conclusions. It must never modify commercial data.

## Current status

**NOT_READY for V1. Eight bounded read-only MCP tools are registered.**

PRD1.16.0 / DEC-039 adds explicit search pagination and optional related lexical
matching to the existing `search_products` tool, plus an external memory-only
MCP catalog/stock consumer. Literal defaults and the eight-tool registry stay
compatible. Duplicate terminal rows now force consistent partial/incomplete
flags in every collector consumer. This extension has offline evidence only;
no ERP/configuration access or Hermes registration change was performed.

PRD1.15.0 / DEC-038 fixes canonical numeric price/stock identity lookups
using closed singleton-ID filters. After separate authorization, both actual
MCP consumers passed one real page1/limit20 query each: HTTP200, one matching
row, nonpartial filtered traversal, same-response fidelity/JSON and completed
cleanup. One memory-only loader read/two attempts were consumed and closed;
no repeat or ongoing access is authorized. Stock array compatibility is
observed only in this bounded installation check, not a supplier schema fix.
The paragraphs below retain the earlier extension and sprint evidence.

PRD1.14.0 / DEC-037 adds stateless listing continuation and `list_inventory`.
The maintainer approved this extension and a separate bounded operational
campaign; execution evidence is recorded in the runbook. Earlier Sprint13
and seven-tool/no-new-query statements below are historical checkpoints,
not the current extension's interface or authorization.

### External MCP catalog/stock campaign

`mcp_consumer.py` is a reusable **consumer**, not a ninth server tool. An
initialized SDK MCP session or an adapter with asynchronous
`call_tool(name, arguments)` returning `CallToolResult` can be supplied by an
authorized host, including a Hermes-side integration. It never discovers
credentials, loads `.env`, opens a transport, persists data or changes Hermes.
The caller owns authorization, session startup/cleanup and safe disclosure.

```python
from mcp_consumer import collect_catalog_inventory

# session is an already initialized, operator-authorized MCP ClientSession.
result = await collect_catalog_inventory(
    session, page_size=50, max_calls=200, max_pages=200,
    max_rows=10_000, timeout_seconds=60,
)
```

These are global ceilings across **both** endpoints, not promised coverage or
permission to query. Defaults are shown above. All are strict positive integers;
page_size is at most50, calls/pages/rows at most1000000, time at most3600 seconds.
Each call uses only `list_products` or `list_inventory`, `max_pages=1`, a fixed
page_size and matching row budget. Server configuration caps still apply. If
the configured row cap is smaller, choose a smaller page_size; the consumer
stops on the tool's safe input error rather than retrying or changing offsets.
It reserves a full page before a call, starts each endpoint at1, validates
contiguous progress/stable totals, and stops on the first anomaly/error/ceiling.
It never issues a speculative page after a known terminal block or a separate
request per catalog identity. Cancellation propagates; timeout returns partial.
The caller must cancel/close its session when appropriate; the module does not
own the SDK transport or claim remote cancellation completion.

`catalog`/`inventory` retain source records and accepted progress; top-level
`rows_received`/`pages_fetched` include structurally reported fetched work even
when a page is rejected, while per-endpoint counters describe accepted pages.
Exact `reduced_id` strings are the sole join key: `001` is not `1`, and neither
is a product_id or business code. `items` has one entry per catalog reduced ID
with `catalog_records`, `inventory_records`, `quantity` and `stock_status`:
positive/zero/negative/unknown/not_found/conflict. No quantities are summed.
Missing stock in an unfinished traversal is unknown; a missing row after a
complete visible stock traversal is not_found, **not zero**. Null/absent quantity
is unknown. Conflicting records remain available but have no confirmed balance;
a block-level source-conflict warning conservatively excludes all identities
in that block because per-row conflict provenance is unavailable. Identical
rows are deduplicated with a warning and make coverage partial. Stock-only
identities appear in `inventory_only_ids` and the inventory source records.

`collection_complete` requires both visible endpoint traversals to finish
safely from1. `partial` also covers unknown/conflicting reconciled quantities;
`complete_dataset` requires both coverage and sufficient reconciled data.
No snapshot, ERP-global visibility, semantic-category coverage, deposit identity,
freshness, availability or delivery guarantee follows. A budget-limited result
is deliberately delivered as partial. Do not persist commercial output by default.

### Resumable listing blocks

`list_products` and `list_inventory` accept `start_page` (strict integer
1–1000000, default1), `max_results` (1–1000, default20), `page_size`
(1–1000/null, must fit the effective row cap) and `max_pages` (1–100,
default1). Configured caps always prevail; the requested page range must
fit the HTTP page bound. Existing seven-tool defaults are unchanged.
Stock listing uses the existing page/limit query, no new remote filter.

Keep page_size fixed across blocks. `first_page`/`last_page` identify fully
validated pages; `next_page` is available only after a safe bounded block.
`block_complete` means this block finished normally, not that all records
were read. `endpoint_exhausted` identifies a valid terminal block.
`complete_dataset` cannot be true for a traversal starting after page1.
Errors, missing pagination, duplicates/conflicts or no progress prevent
safe continuation; data already accepted and safe error codes survive.

An external authorized MCP consumer must reconcile contiguous pages,
stable metadata, received totals and identities across calls before
claiming full visible-endpoint coverage. No transactional snapshot follows.
Catalog/stock association belongs only in that consumer's memory, not in
the normalizer. Stock quantities retain unknown deposit/freshness caveats.
No persistent catalog, new dependency or commercial-write operation is added.
Sprint13 has twenty evidenced tasks under PRD1.13.0 / DEC-036, independently
reviewed without Critical/Important findings. Final sprint/global/G6 acceptance
remains pending; task completion is not release acceptance. Separately
authorized clean installation passed195 tests; one new real MCP listing
page1/limit1 returned HTTP200, one partial item and verified fidelity/JSON/
completed cleanup. Its configuration-read/query budget is consumed and closed.
No broader live tool coverage or V1 acceptance follows. See the
[Sprint13 ledger](docs/runbook.md#sprint-13--final-validation-ledger).

Historical Sprints12/14 checkpoint:
Sprints 12 and 14 consolidate public documentation and the bounded technical
handoff (PRD1.12.0 / DEC-035); they do not execute Sprint 13 or publish a release.
**G5 PASS in the reviewed public-documentation scope; G6 remains pending.**
The current manifest has not been clean-installed in this execution; current
real configuration/ERP acceptance and a platform matrix are not claimed.
Project licensing and a separate Git/index/history publication audit remain
owner actions. No V1_COMPLETE or public distribution clearance is implied.

Sprint 9.5 is complete within its offline local-search/serialization scope; the
bounded real evidence remains PRD DEC-031, which records Sprint 9 complete:
generic SDK discovery of
seven tools and a separately authorized real list_products call through
stdio, page1/limit1, HTTP200. One record returned partial=true/error=null;
same-response fidelity, JSON and completed response/transport/client cleanup
passed. S9.12 is complete; G3 PASS within this bounded scope, not universal
ERP/tool coverage. Sprints 5–8 retain their bounded evidence, including
DEC-027's unvalidated technical SKU.
All real-query budgets remain closed: no new ERP/configuration access,
login, token rotation or Git action is authorized by this work. The later Sprint 10
approval (DEC-033) permits application-only deterministic analyses and
synthetic validation, not real queries or additional MCP tools.
Sprint10 is complete in that offline scope:190 tests and pip check pass,
independent review found no issues, and G4 passes for bounded synthetic
analysis only. No real analysis acceptance or V1 release is claimed.

Sprint 11 is complete within its offline security/quality review scope
(DEC-034):195 tests and pip check pass, independently rerun; no Critical or
Important finding remains. The protected instruction-file update was later
approved and applied after the maintainer requested a renewed submission;
the earlier timeout is resolved. Existing long lines remain documented
Minor style debt. That review did not authorize additional ERP access;
the subsequent approval covers only Sprints 12 and 14 documentation/closure.
The subsequent Sprint13 authorization is limited as stated above; the review
records and remaining evidence limits are in the
[runbook](docs/runbook.md#sprint-11--offline-security-and-quality-review).

The Sprint 9 section below governs current registration. Earlier evidence
sections retain their original no-registration boundaries as history,
not current discovery instructions or renewed real-call budgets.

The private client implements three query POSTs with fixed origin/Host and
closed page/limit bodies. Products may additionally use either integer
idsProdutos=[product_id] or a validated mascara string, never both; prices
may use idsProdutos=[product_id], and stock idsReduzidos=[reduced_id].
Stock's array shape follows official request examples despite the conflicting
number schema; one bounded real array query passed, not a universal contract proof.
No arbitrary filter dict
is accepted. Construction/startup make no ERP request. See the
[sanitized evidence and limits](docs/api-capabilities.md); bounded samples
do not prove global coverage, snapshot, permissions or general readiness.

## Documentation

| Guide | Purpose |
|---|---|
| [Architecture](docs/architecture.md) | Module ownership, Mermaid flow and lifecycle |
| [Configuration](docs/configuration.md) | Variable names, validation, migration and process ownership |
| [Security](docs/security.md) | Literal allowlist, secret handling and limits of guarantees |
| [Local development](docs/local-dev.md) | Windows/macOS/Linux recipes and offline checks |
| [API capabilities](docs/api-capabilities.md#current-implementation-matrix) | Current implemented contracts versus historical evidence/future filters |
| [Runbook](docs/runbook.md) | Troubleshooting, evidence and controlled operational handoff |
| [Licenses and attributions](docs/attributions.md) | Dependency metadata and pending project-license decision |
| [PRD](PRD.md) | Canonical requirements, decisions, sprint checklists and release criteria |

## Architecture

- `config.py`: explicit process-owned settings loader and validation.
- `server.py`: thin MCP stdio entrypoint, one private client per lifespan.
- `mcp_tools.py`: explicit eight-tool registry, strict closed input schemas and safe protocol errors through FastMCP's public list/call hooks.
- `client.py`: HTTPX authentication, literal allowlist, bounded streaming/pagination and safe errors.
- `catalog.py`: immutable normalized records consumed by private collection.
- `tools.py`: bounded commercial consumers with distinct search inspection/output limits, called by MCP adapters without exposing the private client or settings.
- `mcp_consumer.py`: external read-only MCP traversal and exact in-memory catalog/stock reconciliation; no transport/configuration ownership or persistence.
- `analysis.py`: immutable identity preparation and pure aggregation for the two application-only analysis consumers below; no framework or I/O.

IDs/SKU/EAN preserve leading zeros. Decimal prices/quantities serialize as strings; absent/null/zero remain distinct. The projection includes identity, description, classification, EAN, retail/wholesale source prices and tables, quantity, notes, optional source block flag and raw last-change data. Photos, color, size and discount calculations are excluded. Pagination is bounded and reports incomplete/conflicting data as partial; completeness is not an ERP-wide snapshot.

LangChain/LangGraph are not required and are removed from the manifest while unused. The direct analysis pipeline does not justify a framework; queries and analyses need no LLM key.

## Install and start

Requires Python **>=3.14,<4**, one root `.venv` and one root `requirements.txt`. Create the environment only if absent; do not replace an existing one without authorization.

Windows PowerShell (create the environment only if absent; installation is an
intentional operator action, not an offline check):

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe server.py
```

macOS/Linux:

```bash
python3.14 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
./.venv/bin/python server.py
```

These are operator instructions, not new installation verification. Historical clean-install evidence covers the original Sprint 1 manifest on Windows/Python 3.14.3; other platforms and a clean install of the refactored manifest are not implied. The Windows launcher did not select that runtime in the earlier investigation; use an explicitly verified Python 3.14+ interpreter if needed.

Provide `TOKEN_NETONE` and an operator-approved HTTPS `NETONE_BASE_URL`. Supported legacy URLs may derive the origin; all supplied origins must agree. Never overwrite, display or share an existing `.env`. Process overrides do not interpolate or mutate the file/environment. Login/password variables do not enable login. Example hosts/tokens are deliberately non-operational. See [configuration and migration](docs/configuration.md).

Generic MCP client launch configuration (replace only with operator-approved local paths; keep credentials in secure process configuration):

```json
{
  "mcpServers": {
    "netone": {
      "command": "<absolute-path-to-venv-python>",
      "args": ["<absolute-path-to-server.py>"]
    }
  }
}
```

`mcpServers` is a common client configuration convention, not a mandatory MCP
file format. Translate command/args to the chosen client's settings. Use an
absolute Python path from the root .venv and an absolute server.py path;
the loader locates .env beside config.py regardless of the client's cwd.
Process overrides do not prevent the loader from reading an existing root
file. Do not configure credentials through tool arguments or paste them into
this example. See [platform-specific development](docs/local-dev.md).

Expected discovery is exactly the eight tools below. stdout is MCP-only;
stderr emits safe code/component/level diagnostics without raw SDK/HTTP
messages, payloads, exception text or stacks. Loggers are not disabled.
Discovery does not send an ERP query; tools/call does and requires the
operator's authorization. Do not launch a real query to repeat offline QA.

## Sprint 9 MCP interface

The original seven entries are retained below with the DEC-037 eighth
entry and additive continuation contract. Dated evidence later in this
section describes its historical execution, not proof of this extension.

Only these tools are discoverable; all descriptions are in English:

| Tool | Required input | Behavior |
|---|---|---|
| search_products | query: string1–200 | Bounded local casefold substring in description/mask/technical SKU |
| search_product_by_code | code: string1–256 | Preferred business code/SKU: remote mascara filter + exact local equality |
| get_product_details | product_id: integer0–9223372036854775807 | Remote documented product-ID filter; normalized reduced variants |
| search_product_by_ean | ean: string1–256 | Exact local EAN within bounded pages |
| get_product_price | product_id: string1–256 | Canonical numeric ID uses remote idsProdutos; legacy text matches locally; nominal prices, unknown currency |
| check_inventory | reduced_id: string1–256 | Canonical numeric ID uses remote idsReduzidos array; legacy text matches locally; configured-user deposit, unknown identity/freshness |
| list_products | none | Start at page1, at most one page by default |
| list_inventory | none | Bounded stock block; start_page1/one page by default, unknown deposit/freshness |

Every tool accepts strict max_results integer1–1000, capped by configuration
and counting all inspected source rows, not promised matches. search_products
now defaults to100 inspected rows and adds max_items integer1–1000/default20
for returned matches. Explicit max_results20 keeps its old inspection budget;
the other seven tools retain default20. The search's default can reach later
pages when configured caps allow; this deliberately increases coverage/work,
not a promise to search the entire catalog or return20 matches.
Both listings also accept page_size integer1–1000/null, max_pages
integer1–100/default1 and start_page integer1–1000000/default1;
all must fit configured/effective budgets and the page range. Types
are not coerced. Codes preserve zeros, case, spaces and punctuation; blank
and Unicode C-category input is rejected. Query matching trims only input.
Extra arguments are rejected, including URL, endpoint, token, headers,
tenant, method, client and currency. MCP prices default to null currency
with currency_unknown; installation-specific BRL confirmation is not a
model argument or a provider field. DEC-038 adds only the closed identity
filters described below; listing/search defaults and public signatures stay unchanged.

CallToolResult provides structuredContent and equivalent compact JSON text.
Application status error sets isError=true while preserving its safe code;
partial and not_found remain valid structured results. Validation,
unknown-tool and unexpected failures use fixed messages without input or
exception echo. Application input failures use invalid_arguments; unexpected
internal ValueError or serialization failures use tool_error. An explicit
listing page_size exceeding the effective row budget is invalid_arguments
before HTTP, including when the configured cap is smaller than the request.
The application raises ToolInputError (a ValueError subtype) for this case,
rather than exposing the collector's BlockedOperationError.
Cancel a running call with MCP notifications/cancelled;
cancelling only a local SDK task does not send that notification in1.30.0.
Read-only hints are advisory, not credentials or a guarantee of server
internals, repeat safety, availability or delivery. API text is data,
never instructions.

Technical search_product_by_sku remains excluded from MCP under DEC-027.
DEC-039 exposes lexical search through mode=related on search_products, not
as a separate search_products_expanded tool. No analysis/write tool,
arbitrary HTTP/SQL or settings selection is exposed. Existing application
functions remain available independently, with their prior limitations.

SDK mcp==1.30.0 is retained. The [official versioned source](https://github.com/modelcontextprotocol/python-sdk/tree/v1.30.0)
identifies v1.x as a maintained line receiving critical/security fixes,
not the latest stable major. Installed public APIs and protocol behavior
were verified; no upgrade/install or clean-install claim is implied.

Offline checks:149 tests PASS before independent review; pip check PASS.
The generic SDK stdio test uses synthetic settings/responses only and
observes one response close and one client close completing after a single
query. That synthetic check is distinct from the subsequent S9.12 real
observation: one products request, one received/returned row, partial,
HTTP200 and completed cleanup, with no private values retained. The
one-shot budget is consumed and closed, not ongoing query permission.
See the [runbook](docs/runbook.md).

## Development and evidence

### Sprint 10 — deterministic application analyses

These functions are available to an authorized application caller, not
registered MCP tools. Calling them against a real client requires a new
authorized ERP scope; the current sprint used synthetic data only.

- `await tools.analyze_inventory(client, threshold=Decimal('3'),
  max_results=100, max_pages=1)` counts known/unknown quantities and low stock
  (`quantity <= threshold`), zero, negative and above-threshold reduced IDs.
  Zero/negative counts overlap low stock; unknown is never zero or classified.
  The default3 is an approved local rule, not a provider rule. Threshold may
  be a strict nonnegative int or finite nonnegative Decimal (import Decimal
  from decimal), with at most100 coefficient digits and exponent -100..100.
  Strings, floats and bools are rejected; exact Decimal scale is retained.
- `await tools.analyze_product_catalog(client, max_results=100, max_pages=1)`
  counts distinct product IDs among analyzed reduced identities, field
  presence for commercial code/description/technical SKU/EAN, source blocked
  states and exact group/subgroup/line distributions. It does not infer stock,
  sellability, barcode validity, prices or compatibility.

Both perform one bounded collection using only existing page/limit POSTs
(stock or products). max_results is a strict integer1–1000/default100 counting
received rows, including duplicates, not requested distinct products;
max_pages is strict1–100/default1. Configured caps always prevail. Fixed
page size is min(50,effective row budget); one default page can therefore
inspect at most50 rows despite the100-row budget. Later pages require an
explicit max_pages and enough budget for another full fixed-size page.
No new environment variable, filter, join, repeated collection or HTTP
parallelism is added.

Counts use exact reduced_id strings, preserving zeros/spaces/case. Identical
projected records count once; any differing record within an identity group
excludes the whole group from metrics. Source items remain untouched.
records_analyzed is the denominator of per-reduced metrics;
distinct_product_count counts distinct product_id within that universe,
not ERP-wide products. rows_received counts raw rows, source_record_count
and returned_count normalized source records. distinct_reduced_ids includes
conflicting identities; conflicting_identity_count counts excluded groups.
duplicate_records_excluded counts only repeats observable after collector
deduplication, not an inferred count of discarded raw rows.

collection_complete preserves the original collector's completeness.
Analytical complete_dataset additionally requires no error, observed duplicate
or conflicting identity. analysis_scope is sample when incomplete, otherwise
visible_endpoint, never a stable snapshot or global ERP claim. metrics_complete
is separate: no conflicting identities and, for stock, no unknown quantities
among analyzed identities. It can be true for a partial sample or valid empty
universe; it never establishes collection completeness. For catalog it means
field states can be classified, not that the fields are populated.
threshold is an exact string for stock/null for catalog; criteria documents
the calculation rules. Initial/later errors remain error/partial and retain
their safe codes and useful records. All original fields, missing_fields,
Decimal strings and observation timestamps remain. Classifications separate
absent/null/blank counts from actual source-text value/count entries.

Stock deposit/branch identity and freshness remain unknown. No cross-unit or
cross-deposit quantity sums, stock valuation, replenishment recommendation or
delivery promise is produced. The historical O4 ID-filter conflict does not
affect page/limit analysis; DEC-038's provisional directed implementation
does not resolve that supplier documentation conflict. Frameworks/adapters were
evaluated and deliberately omitted: the direct pipeline already serves both
functions. Synthetic execution evidence and review are in the runbook; no
real analysis acceptance, new MCP registration or V1 release is implied.

### Priority: commercial product code (operator's business SKU)

When the operator asks for a product code or business SKU, prefer
`await tools.search_product_by_code(client, code, max_results=20)`.
It queries products with the documented `mascara` filter, then requires
exact equality against normalized product_mask. It does not scan an
unfiltered catalog prefix or fall back silently to another identifier.

Codes are strings of 1–256 characters, nonblank and without Unicode
C-category characters. Leading zeros, case, spaces and punctuation are
preserved. The source mascara/product_mask is the commercial code;
codigoSku/sku is a separate technical field and may be null. The existing
search_product_by_sku still means exact API codigoSku, not this business
alias. IDs/EAN remain separate too. No conversational router
is implemented; search_product_by_code is also registered as described above.

The provider does not document exact-equality semantics for mascara, so
the application checks equality after the bounded filtered traversal.
It reports remote_product_code_exact_match, source-row budgets and the
existing partial/error/completeness metadata. A partial miss is not global
absence; complete_dataset refers only to the provider-visible query.
Product-ID and mask filters cannot be combined. This code lookup never
queries price/stock; their separate directed consumers are described below.

The specifically authorized two-request real check returned HTTP200 twice,
confirmed the supplied code in mascara rather than codigoSku or the IDs,
and exercised this public application function: one exact match, found,
error=null and a complete filtered traversal. No source values are retained
here. The observation is closed, not ongoing request authorization.

### Evidence-based product-field priority

PRD 1.6.0 adds a [field inventory and priority contract](docs/product-field-priority.md)
from 100 received product rows in two approved HTTP200 queries. Commercial
code/description, group/subgroup/line, source block flag and product-source
prices/tables were filled in every sampled row; EAN in 93, notes in 1,
technical codigoSku in none. This is a prefix sample, not global coverage.
A later separately approved page1/limit1 HTTP200 check identified six extra
names: filled unit/packaging metadata and null promotional metadata in
that one row. Names/types/states are recorded in the inventory, not source
values or inferred 100-row frequencies. No additional DTO fields, stock
conversion, promotional pricing or ongoing request permission were added.

The shared immutable projection now adds subgroup, notes,
wholesale_price_table, wholesale_price and strict optional blocked.
JSON presents filled fields first and null/blank fields afterwards without
removing any old keys or values. Zero/false remain filled; absent versus
null remains visible through missing_fields. Read keys by name, not order.
No stock, sellability, currency, final price or discounts are inferred.
No new HTTP consumer, MCP tool, Sprint8 work or technical-SKU acceptance.
Eight new offline tests pass; the full suite passes 116 tests. No private
source values or credentials are stored in the inventory or examples.

### Sprint 8 application functions (also exposed by MCP since Sprint 9)

- `await tools.get_product_price(client, product_id, max_results=20,
  currency=None)` sends idsProdutos=[numeric_id] for a canonical numeric
  textual product ID and validates every returned identity, retaining all
  reduced variants within the original limits. product_id remains a string,
  unlike get_product_details. Retail/wholesale values and tables are source nominal
  amounts, not final quotes, discount calculations or a table choice.
- `currency='BRL'` may be supplied by a trusted caller with operator
  confirmation. It produces currency_source=operator_confirmation, not an
  API currency claim or conversion. The maintainer confirmed BRL for the
  current installation. Generic callers default to unknown currency/null.
- `await tools.check_inventory(client, reduced_id, max_results=20)` selects
  a canonical numeric textual reduced ID using idsReduzidos=[numeric_id]
  and rejects mismatching response pages atomically. Stock is
  documented as physical minus reservations in the user's configured
  deposit. inventory_scope discloses this selection while deposit_id and
  branch_id remain null/unverified. No deposit selection or aggregation.
  Zero, negative, null and absent quantities remain distinct. Raw item
  timestamps are not stock freshness; retrieved_at is local observation.
- Price/stock identities are strings1–256/nonblank/no Unicode C. Only canonical
  ASCII `0|[1-9][0-9]*` text within0–9223372036854775807 is encoded numerically;
  the ceiling is defensive local policy, not a provider quota. Canonical IDs
  above it fail before HTTP. Leading zeros, signs, spaces and other text are
  never stripped: legacy noncanonical IDs retain bounded exact local matching
  with lookup_strategy=bounded_local_exact and numeric_id_filter_unavailable.
  Numeric lookups report lookup_strategy=remote_id_filter. No retry, scalar
  attempt or unfiltered fallback follows an unsuccessful directed request.
  max_results is a strict integer1–1000,
  default20/capped by configuration, counting all received rows. A partial
  miss never proves global absence; initial/later errors remain error/partial.
  found means identity found, not a populated price or sellable quantity;
  missing values produce price_missing/quantity_missing warnings.
- `await tools.list_products(client, max_results=20, page_size=None,
  max_pages=1)` starts at page1 and fetches one page by default. Explicit
  max_pages1–100 is capped by configuration; page_size, when supplied, must
  be a strict positive integer within the effective row budget. None uses
  min(50, effective budget). Fixed page size never shrinks mid-traversal.
  Limits, missing metadata and conflicts remain partial. No arbitrary
  filters, resume cursor, global-catalog or snapshot claim is supported.

All three use only the existing guarded POSTs with closed bodies,
verified TLS, zero retries/redirects and existing byte/time/cleanup bounds.
Calling them needs operator authorization; importing/startup makes no query.
The stock ID-filter schema conflict remains unresolved by the supplier;
DEC-038 chooses the array used in the official operation example and linked
Postman collection. The subsequently authorized real check accepted that array
in this installation, without resolving the supplier's published inconsistency.
Missing metadata/cuts/conflicts remain partial, even with a known zero row;
null/absent quantity is unknown, not zero. Valid terminal empty is not_found
only in the provider-visible query, not proof of zero stock or ERP-wide absence.
Stock conflicts are grouped by reduced_id even when optional product_id differs
or is absent. Incompatible balances remain preserved as partial source rows,
never summed or promoted to a complete confirmed balance.
Documented query intent is accepted under DEC-017, not proof of undisclosed
server internals. No reservation/movement operation is implemented.

The authorized one-shot check on 2026-10-29 used exactly five page1/limit1
requests: two prices, two stock and one products. All returned HTTP200;
get_product_price, check_inventory and list_products each returned one
item, partial=true, complete_dataset=false, error=null. Exact source
projection/numeric/null/absence checks used each consumer's own response
in memory, not equality across changing reads. JSON and all cleanup
completed. No commercial values were retained and no environment file was
modified. This proves only these samples, not broad pagination/snapshot,
deposit identity/freshness or server-internal effects. Budget is closed.

### Bounded literal product search (application and registered MCP tool)

For an operator-authorized caller holding the existing process-owned
NetOneClient, use `await tools.search_products(client, query, max_results=100,
max_items=20)`.
Do not pass settings, URLs, credentials or arbitrary filters as arguments.
Calling the function performs real ERP queries and needs an authorized scope;
importing it or starting stdio does not query the ERP.

The function matches literal case-insensitive substrings in description,
product_mask and sku within a bounded product traversal. It does not send
query/description filters to NetOne, perform semantic search, strip accents
or claim exact-code lookup. query must contain 1–200 characters before
trimming, be nonempty after trimming and contain no Unicode C-category
characters. max_results is a strict integer 1–1000, default 100, also capped
by configured NETONE_MAX_RESULTS. It counts source rows inspected,
including nonmatches/duplicates, not a promised number of matches.
max_items is a separate strict integer1–1000/default20 returned-match ceiling.
The whole bounded traversal is inspected before output selection; no extra
collecting per term or stop at the first match is introduced. Explicit legacy
max_results20 still inspects at most20 rows. list_products remains one page
by default; price/stock/exact identifiers retain their existing row budgets.

Results are JSON-compatible, with exact decimal strings and unchanged
source values. items/returned_count count matches; rows_received counts
the source rows read. local_text_search discloses matching semantics.
inspection_limit/page_limit/page_size/deadline_seconds describe effective
collection ceilings; requested_max_results/requested_max_items describe the
search request and output_limit the effective return ceiling. matched_count
is before output selection; returned_count is actual output. output_truncated
and output_limit_reached identify a cut. collection_complete preserves pre-cut
completeness; a cut makes partial=true and complete_dataset=false even when
collection_complete=true. Errors and useful data survive later failures.
A limited traversal remains partial even with zero matches. not_found is
only possible after a valid complete traversal of the provider-visible
endpoint universe; it does not assert absence from the entire ERP.
Errors remain error/partial with a safe code, never an empty success.
Remote multi-page behavior and snapshot consistency remain unproved.

Synthetic examples (not permission to query ERP): the default with a100-row
cap can inspect page1/limit50 and page2/limit50 and find a record at row51;
max_results20 cannot. A config cap10 always prevails. max_items1 limits
output without changing the inspection budget. A partial miss is inconclusive.

### Expanded lexical search (application and optional MCP mode)

Under DEC-039, Hermes and other MCP clients may call the same `search_products`
tool with mode='related', query='manopla LS2', max_results=100, max_items=20,
page_size=50 and max_pages=2. required_terms/suggested_terms accept lists of
at most20 strings1–200, nonblank/no controls (also nonempty after lexical
normalization). They require related mode. Omit mode to keep literal matching.
start_page defaults to1 (strict1–1000000); max_pages defaults to null (configured
ceiling), or strict1–100; page_size defaults to null (min50/effective row cap),
or strict1–1000 fitting the effective budget. All configured caps prevail;
suffix searches remain partial and terminal metadata prevents extra requests.
These pagination options also work in literal mode. The existing application
expanded helper accepts them too. No remote text filter or new tool is added.


`await tools.search_products_expanded(client, 'manopla LS2', max_results=100,
max_items=20)` may also find a textual `Punho LS2`, using only the reviewed
manopla/punho pair in one collection. required_terms and suggested_terms
remain explicit options. An unambiguous leading reviewed type is separated
from the remaining mandatory description restriction; unknown or ambiguous
phrases stay literal without alternatives/suggestions. For more control,
pass query='manopla', required_terms=('LS2',). This is lexical matching,
not semantic search, confirmed compatibility or synonym equivalence.

Expanded comparisons fold case/accents only in comparison copies and require
word boundaries: LS2 does not match LS20 and punho does not match empunho.
Internal punctuation/metacharacters are literal. Source strings and exact
codes remain unchanged. Direct matches precede reviewed/suggested matches,
with aligned per-item provenance; missing description restrictions are counted
as unverified. Suggestions never enter the reviewed list automatically.
MCP search_products keeps literal defaults; related mode is explicit and
shares the same single bounded collection.

DEC-038 implements the directed numeric filters, while retaining lossless
legacy text lookup. O5 consistently documents ID arrays; O4 still conflicts
between number in its schema and array in its example/Postman collection.
See the [current directed-query evidence](docs/api-capabilities.md#directed-identity-queries--dec-038)
and the separately labelled [historical filter plan](docs/api-capabilities.md#o5o4-reinspection-and-future-directed-query-plan-no-filter-implemented).

Synthetic serialization comparison on the same50-record payload: compact
text24783 bytes versus spaced27017 bytes (8.27% less), with equivalent JSON
and all prior values retained. Redundant amount deepcopy calls dropped200→0.
This is not total MCP wire savings or measured ERP speed. Literal/expanded
fixtures each used2 requests/51 rows/1 match; the old20-row budget used1
request/20 rows/0 matches. More coverage is deliberately more work.

### Product details and exact codes (Sprint 7 application functions)

Implemented and independently task-reviewed; ID/EAN real observations
succeeded, SKU real acceptance remains unverified under DEC-027's accepted
exception. ID/EAN are registered since Sprint 9; technical SKU remains
application-only:

- `await tools.get_product_details(client, product_id, max_results=20)`
  requests the documented product-ID filter and returns the bounded set
  of normalized reduced variants, not the full raw ERP payload.
  product_id must be an exact built-in integer 0–9223372036854775807;
  this defensive local ceiling is not an official provider limit. String
  IDs are rejected rather than silently stripping leading zeros.
- `await tools.search_product_by_sku(client, sku, max_results=20)` matches
  only the API codigoSku field, never the product mask or description.
- `await tools.search_product_by_ean(client, ean, max_results=20)` matches
  only the EAN field. No barcode checksum or remote filter is inferred.

SKU/EAN are strings of 1–256 characters, not whitespace-only and without
Unicode C-category characters. Equality is case-sensitive and preserves
spaces, punctuation and leading zeros; unlike search_products there is
no trimming for matching, casefold or substring matching. Codes are
compared locally in a bounded traversal and disclose local_exact_sku_search
or local_exact_ean_search. They do not solve catalog-wide text search.
max_results counts received source rows, not matches. Missing codes remain
unknown; no match in a partial sample is not proof of global absence.
Errors, metadata, precision and visibility limitations remain unchanged.
No stock/price query or persistent catalog is added by these functions.

Offline unit tests and mocked integration are allowed:

```powershell
.\.venv\Scripts\python.exe -B -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m pip check
```

Use only synthetic settings/responses; no ERP or `.env` access for these checks. Test execution is not remote acceptance. Read-only Git inspection is allowed by PRD policy; version-changing/publishing actions require authorization. No Git action is part of this documentation consolidation.

[Runbook](docs/runbook.md) records the current documentation verification and
historical bounded observations separately. Earlier counts and no-registration
statements above describe their named checkpoints, not the present suite or
new query permission. [Historical archives](docs/history/README.md) retain
superseded policies and evidence; [PRD](PRD.md) owns every sprint state.

## Controlled handoff, not publication

The delivery is NOT_READY, not FOUNDATION_READY / COMMERCIAL_API_BLOCKED:
bounded real commercial evidence already exists, but the final release
criteria are not all established. Sprint13 has current Windows clean-install
and one-shot real listing evidence plus independent review; global acceptance
and the final sprint/G6 gate remain pending. Technical SKU, real acceptance
of directed price/stock filters beyond the two bounded successful checks and
broad coverage retain their explicit limits. Application-only capabilities are
not new tools. AGENTS.md reconciliation for DEC-038 was approved/applied after
the maintainer explicitly requested resubmission; the earlier timeout is resolved
without bypass. The new real-check budget is consumed/closed. See the runbook.

The maintainer may separately choose a project license, review rights and
third-party notices, inspect the Git index/history and exact publication file
set privately, then decide whether to authorize versioning or publication.
No commit, tag, push, repository upload, release or permanent client connection
is performed or authorized by these documentation sprints. Do not stage all
files blindly or rely on .gitignore as evidence that no secret was tracked.
See the [handoff and evidence ledger](docs/runbook.md#sprints-12-and-14--documentation-and-controlled-handoff).
