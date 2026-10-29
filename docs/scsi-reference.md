# SCSI reference audit for Sprint 0

Policy note (PRD 1.2.0): this is a historical source audit, not the current development policy. Offline automated tests and read-only Git inspection are permitted; version-changing Git actions require authorization. LangChain/LangGraph are optional and deferred until a real consumer justifies them. Earlier inspection results remain historical evidence.

Inspection date: 2026-10-27. Scope: NetOne PRD S0.01–S0.03.

The inspected `main` revision is `aaddb90e88987ea2d2bca114e4cdd7c0a0f36ae3`. [Revision evidence](https://api.github.com/repos/pycodebr/scsi/commits/aaddb90e88987ea2d2bca114e4cdd7c0a0f36ae3). Source inspection used read-only GitHub API/raw HTTP, not Git commands, clone, execution or installation. The recursive API tree reported `truncated=false` and identified 34 files in the requested paths. A delegated read-only audit retrieved those files; the coordinator independently reread the cited architecture, tool and graph sections, PRD conventions, environment key names, requirements package names and operational documentation. No upstream source code was copied into NetOne MCP.

This is a reference audit, not certification of the upstream application. Completed checkboxes in upstream planning are not operational evidence. No SCSI component proves NetOne query safety or MCP compatibility, regardless of HTTP method. PRD 1.1.0 permits three documented commercial query POST candidates only, without releasing operations.

## Adopt and adapt

| SCSI evidence at inspected revision | NetOne decision | Boundary |
|---|---|---|
| [PRD: architectural principles, lines 437–443](https://github.com/pycodebr/scsi/blob/aaddb90e88987ea2d2bca114e4cdd7c0a0f36ae3/PRD.md#L437-L443): modular monolith, thin views and services | Keep one process and modules grouped by actual responsibility | `server.py` remains a thin stdio/registry boundary; `tools.py` owns contracts/orchestration; `client.py` owns HTTP/auth/allowlist |
| [Central settings, lines 19–26](https://github.com/pycodebr/scsi/blob/aaddb90e88987ea2d2bca114e4cdd7c0a0f36ae3/core/settings.py#L19-L26): environment-backed configuration | One root `config.py` | No Django import; preserve an existing `.env`; environment/configuration must never come from tool arguments |
| [Tool factory, lines 20–30](https://github.com/pycodebr/scsi/blob/aaddb90e88987ea2d2bca114e4cdd7c0a0f36ae3/ai_agents/tools.py#L20-L30): server-supplied brokerage context captured in tool closures | Inject a process-configured client into typed tools | Process/credential isolation replaces ORM tenant filtering; no tool-selected host, account, route, method or secret |
| [Monetary output, lines 60–68](https://github.com/pycodebr/scsi/blob/aaddb90e88987ea2d2bca114e4cdd7c0a0f36ae3/ai_agents/tools.py#L60-L68) | Decimal values serialized as strings | Use explicit data contracts, not an unrestricted `default=str` fallback |
| [PRD quality conventions, lines 2022–2036](https://github.com/pycodebr/scsi/blob/aaddb90e88987ea2d2bca114e4cdd7c0a0f36ae3/PRD.md#L2022-L2036) | One root `.venv`, one requirements manifest, PEP 8, English identifiers, single quotes, offline and operational validation | NetOne requires Python >=3.14,<4; upstream Python 3.13 is not adopted |
| [Documentation navigation](https://github.com/pycodebr/scsi/blob/aaddb90e88987ea2d2bca114e4cdd7c0a0f36ae3/docs/index.md), [architecture diagram](https://github.com/pycodebr/scsi/blob/aaddb90e88987ea2d2bca114e4cdd7c0a0f36ae3/docs/architecture.md#L7-L39) | Topic-based Markdown, Mermaid, evidence and operational runbook | Public NetOne docs in English; no required documentation build or MkDocs dependency |
| [Environment example](https://github.com/pycodebr/scsi/blob/aaddb90e88987ea2d2bca114e4cdd7c0a0f36ae3/.env.example) and [variable reference](https://github.com/pycodebr/scsi/blob/aaddb90e88987ea2d2bca114e4cdd7c0a0f36ae3/docs/env-vars.md) | Document configuration names by purpose | Values are not copied. NetOne examples use empty credentials and neutral hosts |

## Reject or deliberately improve

| Upstream pattern/evidence | Why it is not transferred |
|---|---|
| Django/Gunicorn, PostgreSQL, RabbitMQ, Redis, Celery and Docker Swarm in [architecture lines 13–50](https://github.com/pycodebr/scsi/blob/aaddb90e88987ea2d2bca114e4cdd7c0a0f36ae3/docs/architecture.md#L13-L50) | Explicitly outside NetOne scope: no web app, ORM/database, background workers, persistent cache, containers or deployment stack |
| Bootstrap/browser UI in [docs index](https://github.com/pycodebr/scsi/blob/aaddb90e88987ea2d2bca114e4cdd7c0a0f36ae3/docs/index.md) | MCP stdio has no web UI, templates, static assets or design system |
| Chat session/message models and persistent task writes in [models](https://github.com/pycodebr/scsi/blob/aaddb90e88987ea2d2bca114e4cdd7c0a0f36ae3/ai_agents/models.py#L6-L42) and [tasks](https://github.com/pycodebr/scsi/blob/aaddb90e88987ea2d2bca114e4cdd7c0a0f36ae3/ai_agents/tasks.py#L49-L82) | NetOne is not a conversational/autonomous agent, has no persistent chat memory and cannot modify commercial records |
| Graph scaffold in [agents lines 113–154](https://github.com/pycodebr/scsi/blob/aaddb90e88987ea2d2bca114e4cdd7c0a0f36ae3/ai_agents/agents.py#L113-L154) | `load`, `fetch`, `prompt` return state unchanged. The inspected `run_summary_agent` [lines 157–184](https://github.com/pycodebr/scsi/blob/aaddb90e88987ea2d2bca114e4cdd7c0a0f36ae3/ai_agents/agents.py#L157-L184) calls the LLM directly, unlike the flow in [docs lines 18–26](https://github.com/pycodebr/scsi/blob/aaddb90e88987ea2d2bca114e4cdd7c0a0f36ae3/docs/ai-agents.md#L18-L26). NetOne only creates `analysis.py` for real deterministic multistep analysis |
| Hardcoded LLM in the inspected summary paths | Basic NetOne tools cannot require an LLM API key; no model provider or chat machinery is copied |
| `qs[:20]` without completeness in [tools lines 25–30](https://github.com/pycodebr/scsi/blob/aaddb90e88987ea2d2bca114e4cdd7c0a0f36ae3/ai_agents/tools.py#L25-L30) | Bounded queries are useful, but NetOne must explicitly label truncation/partial data and preserve the analyzed universe |
| Free-text exception/result mixing in [tools lines 37–49](https://github.com/pycodebr/scsi/blob/aaddb90e88987ea2d2bca114e4cdd7c0a0f36ae3/ai_agents/tools.py#L37-L49) | Use typed `found`, `not_found`, `partial`, `error`; never serialize raw exception text or confuse authentication failure with no results |
| Tool list in [AI docs lines 83–97](https://github.com/pycodebr/scsi/blob/aaddb90e88987ea2d2bca114e4cdd7c0a0f36ae3/docs/ai-agents.md#L83-L97) differs from [returned registry lines 194–198](https://github.com/pycodebr/scsi/blob/aaddb90e88987ea2d2bca114e4cdd7c0a0f36ae3/ai_agents/tools.py#L194-L198) | Documentation must describe actual approved NetOne registrations, not candidate tools or upstream promises |
| Upstream [requirements](https://github.com/pycodebr/scsi/blob/aaddb90e88987ea2d2bca114e4cdd7c0a0f36ae3/requirements.txt) include both HTTP clients and excluded infrastructure, without MCP SDK | Do not copy the manifest; NetOne must independently verify Python 3.14 compatibility, one HTTP client and maintained MCP SDK independently |
| Git, example-to-env copy, Docker and migrations in [local development guide](https://github.com/pycodebr/scsi/blob/aaddb90e88987ea2d2bca114e4cdd7c0a0f36ae3/docs/local-dev.md) | Read-only Git inspection is now permitted; version-changing actions need authorization. No environment overwrite, Docker or database setup |
| Existing upstream tests/migrations in tree | NetOne 1.2.0 permits offline unittest/mocks independently of upstream tests; database migrations remain outside scope |

## Retrieved file inventory

Empty initializer files are included in the tree inventory. Retrieval is not an exhaustive security or functional audit of every file. Each path is relative to the pinned upstream revision above.

```text
PRD.md
.env.example
requirements.txt
core/__init__.py
core/asgi.py
core/celery.py
core/settings.py
core/urls.py
core/wsgi.py
ai_agents/__init__.py
ai_agents/admin.py
ai_agents/agents.py
ai_agents/apps.py
ai_agents/migrations/0001_initial.py
ai_agents/migrations/__init__.py
ai_agents/models.py
ai_agents/tasks.py
ai_agents/tests.py
ai_agents/tools.py
ai_agents/urls.py
ai_agents/views.py
docs/ai-agents.md
docs/architecture.md
docs/backup.md
docs/celery-tasks.md
docs/deploy.md
docs/domain-model.md
docs/env-vars.md
docs/index.md
docs/local-dev.md
docs/multi-tenant.md
docs/permissions.md
docs/protected-media.md
docs/runbook.md
```

## Sprint boundary

S0.01–S0.03 have documentary evidence. This historical audit itself delivered no application module, requirements manifest, environment replacement, MCP registry or installation. Later offline implementation is described in the current README/runbook, not certified by the source audit. The API decision is separately recorded in [api-capabilities.md](api-capabilities.md): G0 BLOCKED.
