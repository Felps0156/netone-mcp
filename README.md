# NetOne MCP

A Python MCP stdio foundation for authorized, strictly read-only NetOne ERP queries and deterministic catalog/inventory analysis. It must never modify commercial data.

## Current status

**NOT_READY for V1. No MCP commercial tools are registered.** Sprints 5–8 are complete; Sprint 7 retains DEC-027's technical-codigoSku exception. PRD 1.8.0 / DEC-029 records Sprint 8's 139-test offline suite and five minimal real HTTP200 queries. Each new public consumer returned one item with correct partiality and accepted source fidelity/cleanup. The observation budget is closed; no further ERP call or Sprint 9 is authorized. Historical results below retain their original scope.

The private client implements three documented query POSTs with fixed origin/Host and closed `page`/`limit` filters. Sprint 7 adds only a products-specific integer product_id encoded as idsProdutos=[product_id], not a caller-supplied filter dictionary. Construction and startup make no ERP request. `tools.search_products` is callable application functionality, not an MCP registration. Its completed Sprint 6 observation returned HTTP 200 twice, including one matching item with correct partiality. See the [sanitized evidence and limits](docs/api-capabilities.md); bounded samples do not prove complete pagination, all permissions or general readiness.

## Architecture

- `config.py`: explicit process-owned settings loader and validation.
- `server.py`: thin MCP stdio entrypoint, empty registry, one private client per lifespan.
- `client.py`: HTTPX authentication, literal allowlist, bounded streaming/pagination and safe errors.
- `catalog.py`: immutable normalized records consumed by private collection.
- `tools.py`: bounded text/code searches, ID-filtered details, local exact price/stock selection and bounded product listing; no MCP query or analysis tool is registered.

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

Expected discovery is an empty tool list, not a working commercial query. stdout is MCP-only; stderr emits safe code/component/level diagnostics without raw SDK/HTTP messages, payloads, exception text or stacks. Loggers are not indiscriminately disabled. Application diagnostics may remain specific and sanitized.

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

### Bounded product search (application function, not an MCP tool)

For an operator-authorized caller holding the existing process-owned
NetOneClient, use `await tools.search_products(client, query, max_results=20)`.
Do not pass settings, URLs, credentials or arbitrary filters as arguments.
Calling the function performs real ERP queries and needs an authorized scope;
importing it or starting stdio does not query the ERP.

The function matches literal case-insensitive substrings in description,
product_mask and sku within a bounded product traversal. It does not send
query/description filters to NetOne, perform semantic search, strip accents
or claim exact-code lookup. query must contain 1–200 characters before
trimming, be nonempty after trimming and contain no Unicode C-category
characters. max_results is a strict integer 1–1000, default 20, also capped
by configured NETONE_MAX_RESULTS. It counts source rows inspected,
including nonmatches/duplicates, not a promised number of matches.

Results are JSON-compatible, with exact decimal strings and unchanged
source values. items/returned_count count matches; rows_received counts
the source rows read. local_text_search discloses matching semantics.
A limited traversal remains partial even with zero matches. not_found is
only possible after a valid complete traversal of the provider-visible
endpoint universe; it does not assert absence from the entire ERP.
Errors remain error/partial with a safe code, never an empty success.
Remote multi-page behavior and snapshot consistency remain unproved.

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
