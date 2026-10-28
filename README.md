# NetOne MCP

NetOne MCP is a planned read-only MCP server for authorized NetOne ERP queries. It will not modify commercial data.

## Current status

The stdio server validates process-owned configuration before starting with an empty tool registry. The private HTTPX client uses an internal allowlist for three documented POST queries with closed page/limit filters, fixed origin and bounded response handling. It does not register commercial tools or make a request at startup. G0 and full G1 remain BLOCKED pending real-world validation; offline checks do not validate a real token, TLS handshake or operator installation. No real query is authorized merely by the internal implementation. See [the capability inventory](docs/api-capabilities.md) for the evidence and outstanding safety gates.

## Requirements and security

The project targets Python 3.14 or newer, below Python 4, with one virtual environment at `.venv`. A clean installation of the original six direct dependencies was verified on Windows with Python 3.14.3 in Sprint 1; Sprint 3 verifies the installed expanded manifest, not a new clean installation. Never share credentials, and do not overwrite an existing `.env`. The example file contains neutral placeholders only.

On the existing Windows environment, install with `.venv\Scripts\python.exe -m pip install -r requirements.txt` and start the empty stdio server with `.venv\Scripts\python.exe server.py`. Configuration must be valid before startup; configuration or client-lifecycle failures return exit code 1 with a sanitized message on stderr. This server does not query NetOne. AnyIO, already required by the SDK, is now a pinned direct dependency for cancellation-safe cleanup; current installed pins and `pip check` were verified, not a new clean installation in Sprint 3.

Provide `TOKEN_NETONE` and an HTTPS `NETONE_BASE_URL` through operator configuration. Existing supported legacy URLs can supply the origin instead; all configured origins must agree and resource paths must match exactly. Process variables override the preserved root `.env`, without modifying either source. Login/password variables do not enable login. The example host is intentionally non-operational, and its empty token is not valid configuration.

See [configuration and migration](docs/configuration.md) for variables, defaults, allowed ranges, security boundaries and migration without rewriting `.env`. Local validation found that the existing legacy reduced-products URL is rejected; the file was preserved and its values were not displayed. Offline synthetic configuration passed, but this does not establish operational readiness for the current installation.

The dedicated stdio process owns root/MCP logging: inherited handlers are replaced with a stderr-only sink rendering fixed diagnostics, without SDK payloads, validation input or tracebacks. HTTPX/httpcore raw diagnostics are suppressed separately. This deliberately reduces debug detail to prevent malformed client input from entering logs; it does not alter MCP protocol responses.

See [the runbook](docs/runbook.md) for current environment findings and [PRD.md](PRD.md) for the canonical project requirements and sprint checklist.
