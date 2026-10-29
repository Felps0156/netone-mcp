# NetOne MCP agent instruction proposal — applied

**Applied after renewed approval.** The maintainer explicitly authorized resubmitting the protected edit, and the normal patch tool accepted it. The sections below are now installed in root `AGENTS.md`; use that file as the authoritative agent context. The earlier timeout is historical, not an active blocker. This update does not authorize ERP calls or advance a sprint.

## Scope and current status

Read `PRD.md` before architectural/sprint work. NetOne MCP is a read-only stdio foundation: empty commercial tool registry, no ERP/login authorization, Sprint 5 partial with S5.01 pending, no Sprint 6. G0/full G1 and operator readiness remain BLOCKED. Offline evidence does not validate credentials, real TLS or provider behavior. History archives are evidence from their time, not current policy.

## Boundaries

- `config.py` is the sole explicit loader/validator. Process variables override root dotenv without interpolation/environment mutation; imports perform no configuration I/O. Settings are immutable, token SecretStr, URL/token excluded from repr; never serialize settings.
- `server.py` is thin stdio/registry/lifespan. One private HTTPX client per lifespan; no startup request. `tools.py` remains documentation-only.
- `client.py` owns token auth, fixed-origin three-POST allowlist, closed page/limit filters, bounded streaming/pagination/errors. `_query()` validates body; request hook checks method/origin/Host/route only. Never remove/bypass the guard for a probe.
- `catalog.py` owns immutable normalization consumed by private collection. Decimal serializes exactly as strings; preserve IDs/leading zeros, text and absent/null/zero. Timestamp stays raw. Duplicates/conflicts and missing metadata must not create false completeness.
- No arbitrary HTTP/SQL/commands, MCP configuration/tenant selection, commercial mutation, persistent cache/DB/UI/Docker/CI or autonomous agent. Analysis frameworks are optional only with a real justified consumer, not scaffolding.

## Security and lifecycle

Preserve `.env` exactly: no display/read/write/move during this refactor. Examples use empty credentials and neutral hosts. Only operator-approved HTTPS configuration, including private/single-label hosts, with fixed origin and verified certificates. No inherited proxy/netrc/CA override, redirects, retries or method/route fallback; legacy retry configuration is inert. No real ERP, login or token regeneration without separate explicit authorization.

Request `identity`, reject compressed success responses, limit raw body to 1 MiB and bound whole-query time/pages/rows. Use public build_request/send(stream=True) and response.stream protocol; no HTTPX state writes. Response and client closure are shielded with one-second bounds. Completed cleanup needs evidence, not merely closed state; a timeout is bounded failure, not release assurance.

stdout is MCP-only. Relevant/root log handlers emit safe level/component/code, never raw SDK/HTTP message/args/exception/stack. Do not indiscriminately disable loggers. Fixed safe application errors may remain specific. Never log settings, environment, headers, bodies or credentials.

## Development and verification

Use Python >=3.14,<4, one root `.venv`, one `requirements.txt`; preserve remaining direct pins and avoid unnecessary installs. LangChain/LangGraph are removed while unused; no LLM key required. English public docs/code/comments/logs; pt-BR PRD/plans; PEP 8, single quotes and Mermaid.

Offline unittest and mocked integration are allowed. Run `.venv/Scripts/python.exe -B -m unittest discover -s tests -v` and relevant safe checks; use only synthetic settings/streams, forbid HTTP sends and real `.env` access. Exercise stdio without LLM. Record actual relevant command/result/limits, not invented success. Update only documentation affected by meaningful decisions; no dossier per microchange. Mark checkboxes only with evidence and never change unrelated sprint states.

PRD policy permits read-only Git inspection, but commits/push/reset/branch changes require authorization; never edit `.git`. This delegated refactor explicitly performs no Git commands. Protected-tool timeout/refusal is a stop, not permission to use another write path. Do not modify another Hermes profile or out-of-scope files.
