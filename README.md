# NetOne MCP

NetOne MCP is a planned read-only MCP server for authorized NetOne ERP queries. It will not modify commercial data.

## Current status

The stdio server validates process-owned configuration before starting with an empty tool registry. Sprint 2 adds typed configuration, validated HTTPS origins, legacy URL compatibility, bounded settings and sanitized startup errors. The HTTP client and commercial tools are not implemented, and no commercial operations are approved. G0 remains BLOCKED. See [the capability inventory](docs/api-capabilities.md) for the evidence and outstanding safety gates.

## Requirements and security

The project targets Python 3.14 or newer, below Python 4, with one virtual environment at `.venv`. A clean installation from `requirements.txt` and imports were verified on Windows with Python 3.14.3. Never share credentials, and do not overwrite an existing `.env`. The example file contains neutral placeholders only.

On the existing Windows environment, install with `.venv\Scripts\python.exe -m pip install -r requirements.txt` and start the empty stdio server with `.venv\Scripts\python.exe server.py`. Configuration must be valid before startup; failures return exit code 1 with a sanitized message on stderr. This server does not query NetOne.

Provide `TOKEN_NETONE` and an HTTPS `NETONE_BASE_URL` through operator configuration. Existing supported legacy URLs can supply the origin instead; all configured origins must agree and resource paths must match exactly. Process variables override the preserved root `.env`, without modifying either source. Login/password variables do not enable login. The example host is intentionally non-operational, and its empty token is not valid configuration.

See [configuration and migration](docs/configuration.md) for variables, defaults, allowed ranges, security boundaries and migration without rewriting `.env`. Local validation found that the existing legacy reduced-products URL is rejected; the file was preserved and its values were not displayed. Offline synthetic configuration passed, but this does not establish operational readiness for the current installation.

See [the runbook](docs/runbook.md) for current environment findings and [PRD.md](PRD.md) for the canonical project requirements and sprint checklist.
