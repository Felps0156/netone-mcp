# NetOne MCP — Agent Instructions

NetOne MCP is a planned Python MCP stdio server for authorized, strictly read-only NetOne ERP queries and deterministic catalog/inventory analysis. The inspected checkout contains `PRD.md`, `.env.example`, `.gitignore`, and a local `.venv`, but no application modules, dependency manifest, README, or `docs/`. Proposed tools and architecture are not implemented functionality.

## Source of truth and scope

- Read `PRD.md` before a sprint or architectural change; its requirements, gates, and sprint checklists are canonical.
- Update affected PRD decisions, risks, roadmap, sprints, and version before implementing scope changes. Mark `[x]` only with verification evidence.
- Do not execute any Git commands, including `git status`, or edit `.git`; versioning belongs to the maintainer (PRD §16.3).
- PRD §3.2 excludes automated tests/fixtures, `tests/`, CI/CD, Docker, databases/ORM, persistent cache/sync, web UI, and autonomous conversational agents.

## Dev environment

- Target Python is `>=3.14,<4`; use one root `.venv` and one root `requirements.txt` when implemented. Dependency versions and compatibility remain unverified.
- Existing `.venv/pyvenv.cfg` records Python **3.12.10**, below the requirement. Resolve replacement with the maintainer; do not silently lower the requirement or create a second environment.
- Planned dependencies include a maintained MCP SDK, LangChain 1.x+, LangGraph, Pydantic, and one HTTP client (`httpx` or `requests`). Basic queries must work without an LLM API key.
- The exact commands below come from PRD §22.3, which labels them **unexecuted examples**, not working setup. Installation/launch require the currently absent `requirements.txt` and `server.py`; environment creation applies only when `.venv` is absent.

Windows PowerShell reference:
```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe server.py
```

macOS/Linux reference:
```bash
python3.14 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
./.venv/bin/python server.py
```

## Build and validation

- No build, test, lint, or formatter configuration/command exists in the inspected checkout. Do not invent one or claim the reference setup has passed.
- PRD §23 prohibits `pytest` and automated test files. Use its VM01–VM20 manual matrix for configuration, stdio, tool discovery, errors, pagination, and data fidelity.
- Record executed scenarios in `docs/runbook.md` when created: date, exact command/scenario, `PASS`/`FAIL`/`BLOCKED`, and sanitized evidence. Remote validation requires explicit authorization and a proven-safe endpoint.

## Planned boundaries and prescribed conventions

No application code exists from which to infer coding conventions. The following are explicit PRD requirements:

- Root `config.py`: sole configuration loader/validator; `client.py`: HTTP, authentication, literal endpoint allowlist, pagination, limits, and sanitized errors.
- Root `tools.py`: typed MCP contracts and query orchestration; `server.py`: thin stdio initialization and approved tool registration.
- Add `analysis.py` only for a justified, real deterministic multistep LangGraph flow. Simple queries must not require a graph or LLM.
- PRD/planning prose is pt-BR; public README/docs, technical identifiers, comments, tool descriptions, and standardized logs are English. PRD specifies PEP 8, single-quoted Python strings, and Mermaid diagrams.
- Monetary values use `Decimal`, serialized as strings; preserve textual IDs/SKU/EAN and leading zeros. Missing stock/price is `null`, not zero.
- Commercial responses distinguish `found`, `not_found`, `partial`, and `error`, with provenance/completeness. Authentication/network failure must not become an empty successful catalog.

## Pitfalls and security gates

- **G0 is unresolved:** the PRD reports legacy commercial **POST** calls, not verified safe GET alternatives. Do not guess GET routes, issue commercial POSTs, hide POST behind a proxy, or register tools for unapproved capabilities.
- Commercial endpoints require a confirmed GET method, evidence of no business side effects, literal-route allowlisting, and authorized validation. Record evidence in `docs/api-capabilities.md` when created; GET alone does not prove safety.
- A documented token-only authentication POST may be allowed separately; it never permits commercial POST. OAuth/refresh support is unconfirmed.
- Preserve any existing `.env` exactly; never display, rewrite, move, or replace it with `.env.example`. `.gitignore` currently excludes only `.venv/` and `.env`.
- `.env.example` must contain only empty credentials and neutral placeholder hosts. Its `example.invalid` URLs are deliberately non-operational. Removing an exposed credential from a file does not revoke it; rotation belongs to the authorized operator.
- Example keys are `TOKEN_NETONE`, `REDUCED_PRODUCTS_URL`, `STOCK_URL`, `LOGIN_NETONE`, and `SENHA_NETONE`; their presence does not prove supported authentication or safe endpoints. `NETONE_BASE_URL` and timeout/limit settings are proposals, not implemented configuration.
- Base URL and credentials belong to process configuration, never MCP arguments. Keep HTTP/authentication inside `client.py`; tools must not accept arbitrary paths, methods, URLs, or tenant selection.
- Reserve stdout exclusively for MCP messages; send sanitized diagnostics to stderr. Bound pages/results/retries, label incomplete analyses as partial, and never fabricate missing records or global metrics.
- With no safe commercial GET, commercial tools remain absent. A completed foundation would be `FOUNDATION_READY / COMMERCIAL_API_BLOCKED`, not `V1_COMPLETE`; this planning-only checkout is not yet a completed foundation.
