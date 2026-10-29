# NetOne MCP

A Python MCP stdio foundation for authorized, strictly read-only NetOne ERP queries and deterministic catalog/inventory analysis. It must never modify commercial data.

## Current status

**NOT_READY / COMMERCIAL_API_BLOCKED. No MCP commercial tools are registered.** Sprints 0–4 have documentary/offline implementation evidence; Sprint 5 is partial: S5.02–S5.14 have offline evidence, while S5.01 still needs installation-specific field confirmation. G0 and full G1 remain BLOCKED. Sprint 6 has not started.

The private client implements three documented query POSTs with fixed origin/Host and closed `page`/`limit` filters. Construction and startup make no ERP request. The internal implementation is not permission to call the ERP, log in or release a tool. See the [API evidence and contracts](docs/api-capabilities.md); synthetic checks do not validate a token, remote TLS, provider behavior or installation readiness.

## Architecture

- `config.py`: explicit process-owned settings loader and validation.
- `server.py`: thin MCP stdio entrypoint, empty registry, one private client per lifespan.
- `client.py`: HTTPX authentication, literal allowlist, bounded streaming/pagination and safe errors.
- `catalog.py`: immutable normalized records consumed by private collection.
- `tools.py`: documentation-only boundary; no query or analysis tool is exposed.

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

Offline unit tests and mocked integration are allowed:

```powershell
.\.venv\Scripts\python.exe -B -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m pip check
```

Use only synthetic settings/responses; no ERP or `.env` access for these checks. Test execution is not remote acceptance. Read-only Git inspection is allowed by PRD policy; version-changing/publishing actions require authorization. No Git action is part of this documentation consolidation.

[Runbook](docs/runbook.md) contains operation, historical evidence links and the executed 51-test refactor validation with its limits. [PRD](PRD.md) owns scope and all sprint checklists. [Historical archives](docs/history/README.md) preserve prior evidence and superseded policies. The approved development policy is installed in `AGENTS.md`; the earlier protected-edit timeout was resolved after renewed approval.
