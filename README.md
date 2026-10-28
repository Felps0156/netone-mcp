# NetOne MCP

NetOne MCP is a planned read-only MCP server for authorized NetOne ERP queries. It will not modify commercial data.

## Current status

The initial stdio server starts with an empty tool registry. Configuration, the HTTP client and commercial tools are not implemented, and no commercial operations are approved. See [the capability inventory](docs/api-capabilities.md) for the evidence and outstanding safety gates.

## Requirements and security

The project targets Python 3.14 or newer, below Python 4, with one virtual environment at `.venv`. A clean installation from `requirements.txt` and imports were verified on Windows with Python 3.14.3. Never share credentials, and do not overwrite an existing `.env`. The example file contains neutral placeholders only.

On the existing Windows environment, install with `.venv\Scripts\python.exe -m pip install -r requirements.txt` and start the empty stdio server with `.venv\Scripts\python.exe server.py`. This server does not query NetOne.

See [the runbook](docs/runbook.md) for current environment findings and [PRD.md](PRD.md) for the canonical project requirements and sprint checklist.
