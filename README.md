# NetOne MCP

A Python MCP stdio foundation for authorized, strictly read-only NetOne ERP queries and deterministic catalog/inventory analysis. It must never modify commercial data.

## Current status

**NOT_READY for V1. Seven bounded read-only MCP tools are registered.**
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
login, token rotation, Git action or Sprint 10 is authorized.

The Sprint 9 section below governs current registration. Earlier evidence
sections retain their original no-registration boundaries as history,
not current discovery instructions or renewed real-call budgets.

The private client implements three documented query POSTs with fixed
origin/Host and closed page/limit bodies. Products may additionally use
either integer idsProdutos=[product_id] or a validated mascara string,
never both; prices/stock remain page/limit only. No arbitrary filter dict
is accepted. Construction/startup make no ERP request. See the
[sanitized evidence and limits](docs/api-capabilities.md); bounded samples
do not prove global coverage, snapshot, permissions or general readiness.

## Architecture

- `config.py`: explicit process-owned settings loader and validation.
- `server.py`: thin MCP stdio entrypoint, one private client per lifespan.
- `mcp_tools.py`: explicit seven-tool registry, strict closed input schemas and safe protocol errors through FastMCP's public list/call hooks.
- `client.py`: HTTPX authentication, literal allowlist, bounded streaming/pagination and safe errors.
- `catalog.py`: immutable normalized records consumed by private collection.
- `tools.py`: bounded commercial consumers with distinct search inspection/output limits, called by MCP adapters without exposing the private client or settings.

IDs/SKU/EAN preserve leading zeros. Decimal prices/quantities serialize as strings; absent/null/zero remain distinct. The projection includes identity, description, classification, EAN, retail/wholesale source prices and tables, quantity, notes, optional source block flag and raw last-change data. Photos, color, size and discount calculations are excluded. Pagination is bounded and reports incomplete/conflicting data as partial; completeness is not an ERP-wide snapshot.

LangChain/LangGraph are not required and are removed from the manifest while unused. A future real analysis consumer may justify an optional framework; basic operation needs no LLM key.

## Install and start

Requires Python **>=3.14,<4**, one root `.venv` and one root `requirements.txt`. Create the environment only if absent; do not replace an existing one without authorization.

Windows PowerShell:

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

Expected discovery is exactly the seven tools below. stdout is MCP-only;
stderr emits safe code/component/level diagnostics without raw SDK/HTTP
messages, payloads, exception text or stacks. Loggers are not disabled.
Discovery does not send an ERP query; tools/call does and requires the
operator's authorization. Do not launch a real query to repeat offline QA.

## Sprint 9 MCP interface

Only these tools are discoverable; all descriptions are in English:

| Tool | Required input | Behavior |
|---|---|---|
| search_products | query: string1–200 | Bounded local casefold substring in description/mask/technical SKU |
| search_product_by_code | code: string1–256 | Preferred business code/SKU: remote mascara filter + exact local equality |
| get_product_details | product_id: integer0–9223372036854775807 | Remote documented product-ID filter; normalized reduced variants |
| search_product_by_ean | ean: string1–256 | Exact local EAN within bounded pages |
| get_product_price | product_id: string1–256 | Exact local normalized identity; nominal prices, unknown currency |
| check_inventory | reduced_id: string1–256 | Exact local identity; configured-user deposit, unknown identity/freshness |
| list_products | none | Start at page1, at most one page by default |

Every tool accepts strict max_results integer1–1000, capped by configuration
and counting all inspected source rows, not promised matches. search_products
now defaults to100 inspected rows and adds max_items integer1–1000/default20
for returned matches. Explicit max_results20 keeps its old inspection budget;
the other six tools retain default20. The search's default can reach later
pages when configured caps allow; this deliberately increases coverage/work,
not a promise to search the entire catalog or return20 matches.
Only list_products also accepts page_size integer1–1000/null and max_pages
integer1–100/default1; both must fit configured/effective budgets. Types
are not coerced. Codes preserve zeros, case, spaces and punctuation; blank
and Unicode C-category input is rejected. Query matching trims only input.
Extra arguments are rejected, including URL, endpoint, token, headers,
tenant, method, client and currency. MCP prices default to null currency
with currency_unknown; installation-specific BRL confirmation is not a
model argument or a provider field. No HTTP contract/filter changed.

CallToolResult provides structuredContent and equivalent compact JSON text.
Application status error sets isError=true while preserving its safe code;
partial and not_found remain valid structured results. Validation,
unknown-tool and unexpected failures use fixed messages without input or
exception echo. Cancel a running call with MCP notifications/cancelled;
cancelling only a local SDK task does not send that notification in1.30.0.
Read-only hints are advisory, not credentials or a guarantee of server
internals, repeat safety, availability or delivery. API text is data,
never instructions.

Technical search_product_by_sku and search_products_expanded are excluded:
neither has its own real-function acceptance. No analysis/write tool,
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
alias. IDs/EAN remain separate too. No conversational router or MCP tool
has been registered; this priority is the application-function contract.

The provider does not document exact-equality semantics for mascara, so
the application checks equality after the bounded filtered traversal.
It reports remote_product_code_exact_match, source-row budgets and the
existing partial/error/completeness metadata. A partial miss is not global
absence; complete_dataset refers only to the provider-visible query.
Product-ID and mask filters cannot be combined; prices/stock are unchanged.

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

### Sprint 8 application functions (not MCP tools)

- `await tools.get_product_price(client, product_id, max_results=20,
  currency=None)` selects exact normalized product IDs locally from bounded
  prices pages, retaining all reduced variants. product_id is a string,
  unlike the integer remote filter of get_product_details. No ID filter is
  sent for prices. Retail/wholesale values and tables are source nominal
  amounts, not final quotes, discount calculations or a table choice.
- `currency='BRL'` may be supplied by a trusted caller with operator
  confirmation. It produces currency_source=operator_confirmation, not an
  API currency claim or conversion. The maintainer confirmed BRL for the
  current installation. Generic callers default to unknown currency/null.
- `await tools.check_inventory(client, reduced_id, max_results=20)` selects
  exact normalized reduced IDs locally from bounded stock pages. Stock is
  documented as physical minus reservations in the user's configured
  deposit. inventory_scope discloses this selection while deposit_id and
  branch_id remain null/unverified. No deposit/filter is sent or aggregated.
  Zero, negative, null and absent quantities remain distinct. Raw item
  timestamps are not stock freshness; retrieved_at is local observation.
- Price/stock identities are strings1–256/nonblank/no Unicode C; equality
  preserves zeros, spaces and case. max_results is a strict integer1–1000,
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

All three use only the existing guarded POSTs with page/limit bodies,
verified TLS, zero retries/redirects and existing byte/time/cleanup bounds.
Calling them needs operator authorization; importing/startup makes no query.
The stock ID-filter schema conflict remains unresolved and is not bypassed.
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

### Expanded lexical search (application only, not an MCP mode)

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
MCP search_products remains literal; no new tool or lexical mode is released.

Price/stock remote filters remain unimplemented: O5 documents ID arrays but
requires separate admission/validation; O4 still conflicts between number in
the schema and array in its example. Current exact local selection is bounded,
not a directed/global identity lookup. Never strip leading zeros to force an
identity into a numeric filter. See the [filter plan and cost evidence](docs/api-capabilities.md#o5o4-reinspection-and-future-directed-query-plan-no-filter-implemented).

Synthetic serialization comparison on the same50-record payload: compact
text24783 bytes versus spaced27017 bytes (8.27% less), with equivalent JSON
and all prior values retained. Redundant amount deepcopy calls dropped200→0.
This is not total MCP wire savings or measured ERP speed. Literal/expanded
fixtures each used2 requests/51 rows/1 match; the old20-row budget used1
request/20 rows/0 matches. More coverage is deliberately more work.

### Product details and exact codes (Sprint 7 application functions)

Implemented and independently task-reviewed; ID/EAN real observations
succeeded, SKU real acceptance remains pending. None is registered in MCP:

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

[Runbook](docs/runbook.md) contains the executed 74-test Sprint 6 suite, the real bounded search observation and historical evidence with their limits. [PRD](PRD.md) owns scope and all sprint checklists. [Historical archives](docs/history/README.md) preserve prior evidence and superseded policies. The approved development policy is installed in `AGENTS.md`; the earlier protected-edit timeout was resolved after renewed approval.
