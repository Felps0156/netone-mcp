# Operations and verification runbook

## Current boundary

PRD 1.2.1 records the completed Sprint 5. The original PRD 1.2.0 refactor authorization was offline only. The maintainer subsequently authorized configuration-loader access in memory and a bounded S5.01 observation; after the operator's local correction and renewed authorization, products/prices/stock each returned one record successfully. This supersedes the earlier configuration failure, not the limits of the original offline evidence. No login, token rotation, commercial tool or Sprint 6 was performed. The registry is empty. G0/full G1 require explicit acceptance for general release; three samples are not ongoing authorization or complete installation readiness.

Current behavior and limits: [configuration](configuration.md). Endpoint contracts, field mapping and unresolved provider ambiguities: [API inventory](api-capabilities.md). Canonical sprint IDs/states/sequence: [PRD section 28](../PRD.md#28-sprints-de-implementação-em-checklist).

## Evidence retained, not re-executed

[The integral runbook through PRD 1.1.6](history/runbook-through-1.1.6.md) preserves every prior command/scenario, PASS/FAIL/BLOCKED result, harness failure, independent finding and correction. [The integral PRD 1.1.6](history/PRD-1.1.6.md) preserves prior requirements/decisions and checklist context. These are immutable historical records; obsolete restrictions and earlier deny-all/GET-only states are not current policy. Relative links inside verbatim archives refer to the original document locations; use [the archive index](history/README.md) for current navigation.

Historical outcome summary (not new verification):

| Scope | Recorded evidence | Remaining limit |
|---|---|---|
| Sprint 0 | Source/document review; S0.11 later accepted under DEC-017 | Query intent is not proof of internal ERP effects |
| Sprint 1 | Original manifest clean install on Windows/Python 3.14.3; empty stdio handshake | Not a clean install of the refactored manifest or other platforms |
| Sprint 2 | Synthetic loader/validation and safe startup; URL-origin compatibility | Historical installation route mismatch, no current `.env` inspection |
| Sprint 3 | Private client/lifespan/shield and logging leak correction | No real token/permissions/DNS/TLS proof |
| Sprint 4 | Restricted three-POST transport, identity/1 MiB, fixed errors, zero replay, G2 offline | Provider compatibility and operational validation unverified |
| Sprint 5 | Exact normalization, bounded collection, duplicates/partiality and cleanup corrections | S5.01 real field evidence pending; no tools, join or analysis |

## Local setup and operation

Use [README setup](../README.md#install-and-start) with one existing compatible root `.venv`. Do not recreate it unless absent or replacement is explicitly authorized. `pip install -r requirements.txt` changes the local environment and is an operator action, not a check to run silently. Start `server.py` only with valid operator-owned configuration. No LLM key is needed.

For this offline refactor, tests must replace the loader/file access with synthetic settings and forbid HTTP sends. In a real operator session, configuration loading reads the root `.env`; this documentation does not authorize such access by the development agent. Never print settings, environment, headers or bodies for diagnosis.

Expected initialize/tools-list response: valid protocol replies with an empty tool list. stdout is exclusively MCP JSON-RPC; safe code/component/level diagnostics go to stderr. Root DEBUG/malformed SDK input must not expose raw messages, validation values, exceptions or stacks. Do not solve logging failures by disabling the protocol or indiscriminately disabling loggers.

## Troubleshooting

| Symptom | Safe response |
|---|---|
| `configuration_error` | Inspect fixed variable/constraint code only; operator corrects secure launch settings, preserving file; do not request secret/URL in chat |
| Empty tool list | Expected foundation state, not failed discovery; do not register candidates to make a demo work |
| 401 / 403 | Distinct authentication/authorization failures; never convert to no results, log in or regenerate token automatically |
| 404 | Endpoint failure, not valid empty catalog |
| 429 / timeout / 5xx | Fixed error or partial prior data; no retry, Retry-After replay, redirect or route/method fallback |
| `invalid_response` | Reject malformed/compressed/oversize/inconsistent page without printing raw content; preserve previous valid data as partial |
| Missing totals / repeated page / budget exhausted | Partial result, no global KPI or invented totals |
| Cancellation / cleanup failure | Preserve cancellation/original error, shield cleanup; bounded stalled-close failure is not completed release |
| Protected instruction edit timeout | Stop; no retry/bypass without renewed user authorization. The refactor's AGENTS timeout was resolved by renewed approval through the normal patch tool. |

## Offline verification commands and acceptance

Windows/Git Bash paths (PowerShell uses equivalent backslashes):

```bash
.venv/Scripts/python.exe -B -m unittest discover -s tests -v
.venv/Scripts/python.exe -m pip check
```

The coordinator checks imports/syntax without configuration reads, effective remaining pins, public file scope/links, baseline preservation and an actual stdio subprocess with synthetic loader, LLM variables removed and HTTP sends forbidden. Windows event-loop socketpair setup must not be accidentally blocked before event-loop creation. Required behavior: two normal initialize/tools-list replies, zero tools, no synthetic secret/origin or raw SDK/HTTP data in stderr; malformed-protocol scenarios must remain safe too.

Tests cover config origin/legacy migration/private hosts, guard/schema/status/JSON/Decimal/bytes, fixed-size pagination and contradictory/no-progress pages, initial/later errors, deadline, cancellation and shielded cleanup. Success of a mock is not VM09 remote acceptance. PRD retains VM01–VM20 for applicable operational acceptance.

## Refactor final validation — 2026-10-28

All data/settings below were synthetic. No Git command, ERP/login call, real `.env` read/write, installation, environment replacement or later-sprint implementation was performed. The Windows root interpreter remains Python 3.14.3. These checks do not establish clean installation, other-platform compatibility, credentials, permissions, remote DNS/TLS, provider schema or absence of server-internal effects.

| Command / exact scenario | Result | Observed evidence |
|---|---|---|
| `.venv/Scripts/python.exe -B -m unittest discover -s tests -v` | PASS | Final suite: 51 distinct tests, no failures. Config, normalizer, actual guarded mock HTTP path, pagination, size/JSON/status errors, deadline/cancellation/cleanup and stdio covered. |
| `.venv/Scripts/python.exe -m pip check` | PASS | `No broken requirements found.` Five remaining manifest pins match installed distribution versions; no version upgrade/install/uninstall performed. LangChain/LangGraph removed only from the manifest. |
| `.venv/Scripts/python.exe -B -c '<source compilation and line-length inspection>'` | PASS | All nine root/test Python sources compiled; no line exceeds 79 characters. No configured external linter/formatter was run. |
| Fresh subprocess imports with `.env` reads and HTTP client construction forbidden; compare environment | PASS | All five application modules import without configuration access, client construction, output or environment mutation. |
| Inspect effective actual HTTPX transport from synthetic Settings; close without send | PASS | Certificate verification CERT_REQUIRED and hostname verification true; zero retries, no redirects/proxy mounts, pool one, four phase timeouts 15 seconds. No remote handshake inferred. |
| Actual stdio subprocess in `tests/test_server.py`, synthetic loader, protected `.env` reads, HTTP sends forbidden, LLM keys removed, LangChain/LangGraph imports blocked, DEBUG | PASS | Initialize/tools-list: two JSON replies, zero tools, exit 0. Malformed initialize followed by valid session: error ID 99 then valid IDs 1/2; no synthetic secret/origin, malformed-input sentinel or traceback exposed. |
| Parse PRD checklist against pre-edit public JSON baseline; compare history and unchanged contracts | PASS | All 212 sprint IDs/order/states unchanged; S5.01 open, no 6+ task completed. Integral PRD/runbook archives match baseline; `catalog.py`, `tools.py`, `AGENTS.md` unchanged. |
| Check local links in current README/PRD/docs/archive index/refactor plan | PASS | No nonexistent target. Verbatim archived links retain their original-location semantics, explained in the history index. |
| Read `.env.example` only; inspect placeholder credential assignments | PASS | Empty token/login/password, neutral example.invalid hosts; retry input explicitly marked legacy/inert. This is not access to `.env`. |

Baseline and regression sequence: 18 client + five catalog characterization tests passed before production edits. New architecture/logger/bounded-client-cleanup criteria failed on the original behavior, then passed. Configuration had 11 initial characterization tests plus newly failing desired behaviors before its implementation. A concurrent early child suite saw the three intentional RED client tests; later integrated runs resolved them. Final counts supersede those intermediate runs, not historical sprint results.

Independent read-only review executed the 49-test pre-fix suite twice (49 distinct tests, not 98), plus DEBUG malformed-protocol recovery, canonical IPv6/port/origin guard probes, stalled response cleanup, syntax, pip consistency and baseline checks. It found one Important issue, no Critical/Minor: `NetOneClient.__aexit__()` could let a stalled client-close timeout replace the active body exception or AnyIO cancellation. The coordinator reproduced both cases in two new failing tests, then changed exit handling to preserve the incoming exception/cancellation while still reporting standalone cleanup failure. Final 51/51 suite passed after that fix. This is execution verification, not a second independent review. No review finding is deferred.

Remaining deliberate trade-offs: explicit public AsyncByteStream iteration is retained to keep the first close inside the bounded shield without writing HTTPX state; it avoids the installed `aiter_raw()` auto-close race. Input filters are validated once by `_query()` and the closed body is built internally; the destination hook is not a sandbox against trusted code deliberately accessing the private HTTP client. Response/client closes that exceed the one-second allowance are bounded failures, not completed-release guarantees. Raw third-party diagnostics remain withheld; component/level/event identity is available.

The baseline audit above preceded the final instruction update: `AGENTS.md` was unchanged at that checkpoint. After the maintainer returned and explicitly authorized a new protected-edit request, the normal patch tool applied the approved instruction sections to root `AGENTS.md`. [The proposal record](agent-instructions-proposed.md) is now marked applied. The timeout is resolved, not an active pending update. No ERP/login, secret access or later sprint was authorized by this follow-up; related current status references were reconciled.

## Operational unblock

Maintainer owns safe configuration, account permissions and provider clarification of the API conflicts. Only after security review and explicit bounded-call authorization may a real documented-method validation be considered; it can precede tool release but is not permission for login, scanning or tool registration. Record sanitized schema/status/completeness without records/secrets; HTTP 200 alone does not prove absence of internal business effects. Do not require a GET equivalent or bypass TLS/guards.

## Historical initial S5.01 observation attempt — 2026-10-29

The maintainer explicitly authorized the existing loader to read the root
environment file in memory, without modification or disclosure, for up to
three queries: products, prices and stock, each with page=1 and limit=1.
No retries, login, token rotation, tools or Sprint 6 were authorized.
Only known field presence/nullability/types could be recorded; no private
origin, credential, response body or commercial value could be persisted.

Preflight: `.venv/Scripts/python.exe -B -m unittest discover -s tests -v`
passed all 51 tests. A one-shot probe in the managed scratch directory
used the existing loader, safe logging and guarded client path. Both
configuration-only attempts stopped before constructing the client or
sending a request. The second included the loader's fixed diagnostic:
`REDUCED_PRODUCTS_URL must be a valid HTTPS URL with the expected path.`
This does not identify which URL constraint failed; no private value was
printed or retained. The environment file was not written or moved.

Result at that checkpoint: BLOCKED before network activity, zero ERP
requests, no real field evidence. S5.01 was open. This initial configuration
blocker was superseded by the successful observation below. The operator
needed to correct the configuration to an approved HTTPS origin and the exact
documented legacy route, consistently across supplied URL variables,
without sharing the values in chat. No automatic URL rewrite, ignored
legacy variable, HTTP fallback or TLS bypass was attempted. Configuration
changes and a renewed bounded attempt require an operator decision.

## Successful S5.01 field observation — 2026-10-29

The maintainer removed the optional legacy URL variables locally and
renewed permission to load private configuration without disclosure and
perform the bounded validation. No environment file was written, moved or
displayed by the agent. The existing token was sufficient; login/password
were not used for authentication, and no token was obtained or rotated.

Command: `.venv/Scripts/python.exe -B <managed-scratch>/netone_s5_validation.py`.
Observation began at 16:41:30 UTC. The probe used `load_config()`, existing
safe logging and one `NetOneClient`; it called `_query(operation, 1, 1)`
once for each operation, preserving the original guard and transport.

| Method / literal route | Request body | Observed result |
|---|---|---|
| POST `/app-web/api/v2/produto/reduzidos` | page=1, limit=1 | Successful 2xx JSON envelope, one record, normalizer accepted |
| POST `/app-web/api/v2/produto/precos` | page=1, limit=1 | Successful 2xx JSON envelope, one record, normalizer accepted |
| POST `/app-web/api/v2/produto/estoque` | page=1, limit=1 | Successful 2xx JSON envelope, one record, normalizer accepted |

All three had integer page/totalPages/totalElements/total fields; the
first-page metadata validator accepted them. Only known field names and
absent/null/type categories were retained; the complete sanitized matrix
is in [the API inventory](api-capabilities.md#s501-real-field-evidence--2026-10-29).
No raw response, private origin, credential, commercial value or arbitrary
response key was persisted in the repository or scratch report.

HTTPS certificate/hostname verification, fixed origin/Host/routes,
identity encoding, 1 MiB response limit and existing deadlines remained
enabled. Exactly three application queries, with zero retries or redirects,
were performed. Response cleanup completed before each return and client
cleanup completed before the probe reported completion.

After the observation, `.venv/Scripts/python.exe -B -m unittest discover
-s tests -v` passed all 51 offline tests, including actual stdio discovery
with an empty registry and blocked HTTP sends. No application code or
dependency was changed for this validation. PRD 1.2.1 marks only S5.01 as
newly complete; the existing S5.02–S5.14 evidence and sprint-specific
precision/nullability criteria complete Sprint 5.

Limits: only one record per endpoint was inspected, without asserting a
common identity. No real multi-page traversal, full-catalog completeness,
snapshot stability, deposit identity, currency, timestamp semantics,
least-privilege granularity or undisclosed internal effects were proved.
The existing header/token and verified TLS worked for these requests;
G0/full G1 still require an explicit general-release acceptance review,
not a claim that access remains wholly unverified. Tools, login, ongoing
calls and Sprint 6 are not released by this result.
