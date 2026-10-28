# NetOne MCP — Agent Instructions

NetOne MCP is a Python MCP stdio foundation for authorized, strictly read-only NetOne ERP queries and deterministic catalog/inventory analysis. Sprint 2 implements explicit typed configuration and sanitized startup validation; `client.py` and `tools.py` remain documentation-only boundaries. No commercial tool or operation is released. PRD 1.1.1 retains the maintainer-authorized admission of three documented query POST candidates; commercial mutation remains prohibited. Sprint 0 has 15 verified tasks and S0.11 blocked pending semantic-safety evidence; G0 = BLOCKED pending safety/runtime validation, not because GET is missing. See `docs/configuration.md`, `docs/api-capabilities.md`, `docs/scsi-reference.md`, and `docs/runbook.md`.

## Source of truth and scope

- Read `PRD.md` before a sprint or architectural change; its requirements, gates, and sprint checklists are canonical.
- Update affected PRD decisions, risks, roadmap, sprints, and version before implementing scope changes. Mark `[x]` only with verification evidence.
- Do not execute any Git commands, including `git status`, or edit `.git`; versioning belongs to the maintainer (PRD §16.3).
- PRD §3.2 excludes automated tests/fixtures, `tests/`, CI/CD, Docker, databases/ORM, persistent cache/sync, web UI, and autonomous conversational agents.

## Dev environment

- Target Python is `>=3.14,<4`; use one root `.venv` and one root `requirements.txt`. Clean installation and imports of the pinned direct dependencies were verified on Windows with Python 3.14.3; other platforms and transitive versions remain unverified.
- The maintainer authorized replacement of the former incompatible environment; the root `.venv` now uses Python 3.14.3. Do not silently lower the requirement or create a second environment.
- Planned dependencies include a maintained MCP SDK, LangChain 1.x+, LangGraph, Pydantic, and one HTTP client (`httpx` or `requests`). Basic queries must work without an LLM API key.
- The commands below are PRD §22.3 examples. Installation and stdio startup were verified using the existing Windows `.venv`; `py -3.14` did not select the installed Python 3.14 runtime in the earlier inspection. Environment creation applies only when `.venv` is absent.

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

Executable application code validates configuration and initializes an empty MCP server. The following are explicit PRD requirements:

- Root `config.py`: sole configuration loader/validator; `client.py`: HTTP, authentication, literal endpoint allowlist, pagination, limits, and sanitized errors.
- Root `tools.py`: typed MCP contracts and query orchestration; `server.py`: thin stdio initialization and approved tool registration.
- Add `analysis.py` only for a justified, real deterministic multistep LangGraph flow. Simple queries must not require a graph or LLM.
- PRD/planning prose is pt-BR; public README/docs, technical identifiers, comments, tool descriptions, and standardized logs are English. PRD specifies PEP 8, single-quoted Python strings, and Mermaid diagrams.
- Monetary values use `Decimal`, serialized as strings; preserve textual IDs/SKU/EAN and leading zeros. Missing stock/price is `null`, not zero.
- Commercial responses distinguish `found`, `not_found`, `partial`, and `error`, with provenance/completeness. Authentication/network failure must not become an empty successful catalog.

## Pitfalls and security gates

- **G0 = BLOCKED:** PRD 1.1.0 replaces GET-only policy with read-only business semantics. Only POST `/app-web/api/v2/produto/reduzidos`, POST `/app-web/api/v2/produto/precos`, and POST `/app-web/api/v2/produto/estoque` are admitted commercial policy candidates, not runtime-approved operations. The seven auxiliary Product queries are inventoried only. S0.11 remains unchecked; never infer GET alternatives, generic POST permission or tool release from this revision.
- Commercial operations require documented exact method + literal route + closed typed query/filter schema, evidence of no business mutation, safe configuration/transport and authorized validation before operational allowlisting/tool release. Reject arbitrary payload fields, URL, method, route, headers and tenant in MCP inputs. Neither GET nor POST alone proves safety. POST query retries default to zero (including ambiguous timeout), automatic commercial redirects are disabled, and method/route fallback is forbidden; retries require specific repeat-safety evidence. Record evidence in `docs/api-capabilities.md`.
- Official documentation describes the user token in `netone-auth-token`, obtainable from ERP settings or POST `/app-web/api/v2/auth/login` with `usuario` and `senha`. No authentication call was made. Token-only authentication is separate from commercial query admission and does not permit arbitrary POST. OAuth/refresh/expiry support is unconfirmed. Header rendering conflicts and other contract ambiguities are recorded in `docs/api-capabilities.md`. The policy revision authorizes documentation only, not login, real API calls or another sprint.
- Preserve any existing `.env` exactly; never display, rewrite, move, or replace it with `.env.example`. `.gitignore` excludes `.venv/`, environment variants, logs and common local Python artifacts.
- `.env.example` must contain only empty credentials and neutral placeholder hosts. Its `example.invalid` URLs are deliberately non-operational. Removing an exposed credential from a file does not revoke it; rotation belongs to the authorized operator.
- `config.load_config()` reads only recognized configuration from the root `.env`, then overlays process variables without interpolation or environment mutation. `TOKEN_NETONE` is required; `LOGIN_NETONE` and `SENHA_NETONE` are ignored. A validated HTTPS base can be derived from exact legacy routes, with all origins required to agree. Defaults/ranges and migration are in `docs/configuration.md`. Settings omit URL/token from repr and store the token as `SecretStr`; never serialize settings. The existing local reduced-products URL fails validation and remains unchanged; offline synthetic acceptance does not mean installation readiness or G1 completion.
- Base URL and credentials belong to process configuration, never MCP arguments. Keep HTTP/authentication inside `client.py`; tools must not accept arbitrary paths, methods, URLs, or tenant selection.
- Reserve stdout exclusively for MCP messages; send sanitized diagnostics to stderr. Bound pages/results/retries, label incomplete analyses as partial, and never fabricate missing records or global metrics.
- Without a proven-safe and validated commercial query operation, tools remain absent, regardless of method. A completed foundation would be `FOUNDATION_READY / COMMERCIAL_API_BLOCKED`, not `V1_COMPLETE`; Sprint 1 alone does not complete the broader foundation. No checklist status was changed by the PRD 1.1.0 policy revision.
