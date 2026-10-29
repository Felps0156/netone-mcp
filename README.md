# NetOne MCP

A Python MCP stdio foundation for authorized, strictly read-only NetOne ERP queries and deterministic catalog/inventory analysis. It must never modify commercial data.

## Current status

**NOT_READY for V1. No MCP commercial tools are registered.** Sprints 5 and 6 are complete. Sprint 6's bounded local search passed 74 offline tests, real-call checks and independent reviews; both non-blocking review findings were corrected. G0/G1 PASS only for the product page/limit operation, based on accepted query intent, transport safeguards and real token/TLS evidence. Later sprints remain unstarted.

The private client implements three documented query POSTs with fixed origin/Host and closed `page`/`limit` filters. Construction and startup make no ERP request. `tools.search_products` is callable application functionality, not an MCP registration. Its explicitly authorized two-request Sprint 6 observation returned HTTP 200 twice, including one matching item through the function with correct partiality. No login or environment-file modification was needed. See the [sanitized evidence and limits](docs/api-capabilities.md); bounded samples do not prove complete pagination, all permissions or general readiness.

## Architecture

- `config.py`: explicit process-owned settings loader and validation.
- `server.py`: thin MCP stdio entrypoint, empty registry, one private client per lifespan.
- `client.py`: HTTPX authentication, literal allowlist, bounded streaming/pagination and safe errors.
- `catalog.py`: immutable normalized records consumed by private collection.
- `tools.py`: Sprint 6 adds callable local `search_products` orchestration; no MCP query or analysis tool is registered.

IDs/SKU/EAN preserve leading zeros. Decimal prices/quantities serialize as strings; absent/null/zero remain distinct. The projection includes identity, description, group/line, EAN, price, stock and raw last-change data, plus separate API SKU and price-table provenance. Photos, color, size, wholesale and discounts are excluded. Pagination is bounded and reports incomplete/conflicting data as partial; completeness is not an ERP-wide snapshot.

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

Offline unit tests and mocked integration are allowed:

```powershell
.\.venv\Scripts\python.exe -B -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m pip check
```

Use only synthetic settings/responses; no ERP or `.env` access for these checks. Test execution is not remote acceptance. Read-only Git inspection is allowed by PRD policy; version-changing/publishing actions require authorization. No Git action is part of this documentation consolidation.

[Runbook](docs/runbook.md) contains the executed 74-test Sprint 6 suite, the real bounded search observation and historical evidence with their limits. [PRD](PRD.md) owns scope and all sprint checklists. [Historical archives](docs/history/README.md) preserve prior evidence and superseded policies. The approved development policy is installed in `AGENTS.md`; the earlier protected-edit timeout was resolved after renewed approval.
