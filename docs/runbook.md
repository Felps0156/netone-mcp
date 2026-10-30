# Operations and verification runbook

## Current boundary

PRD 1.9.1 / DEC-031 records Sprint 9's completed MCP integration:
seven evidenced application consumers are registered, excluding technical
SKU and expanded search. S9.12's separately authorized single real listing
passed via generic MCP stdio, page1/limit1, HTTP200, one partial item and
completed response/transport/client cleanup. G3 PASS in that bounded scope;
Sprint9 complete, V1 NOT_READY. The memory-only loader read and one-query
budget are consumed and closed; no further .env access, ERP query, login,
token rotation, .env write, Git action or Sprint10 is authorized.
All earlier observation budgets remain closed. Earlier no-registration/
no-Sprint9 statements and test counts below describe historical checkpoints;
the Sprint9 section governs current discovery. BRL remains installation
context in the application, not a generic MCP currency or API field.

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

Offline tests must replace loader/file access with synthetic settings and forbid HTTP sends. DEC-029's separate memory-only loader read was consumed by the completed Sprint8 probe, without modification/disclosure; no subsequent reads are authorized. Never print settings, environment, headers or bodies for diagnosis.

Expected initialize/tools-list: valid protocol replies with exactly
search_products, search_product_by_code, get_product_details,
search_product_by_ean, get_product_price, check_inventory and list_products.
Startup/discovery make no ERP request; authorized tools/call does. stdout
is exclusively MCP JSON-RPC; safe code/component/level diagnostics go to
stderr. Malformed SDK input must not expose raw values/exceptions/stacks.
Do not disable the protocol or indiscriminately disable loggers.

## Troubleshooting

| Symptom | Safe response |
|---|---|
| `configuration_error` | Inspect fixed variable/constraint code only; operator corrects secure launch settings, preserving file; do not request secret/URL in chat |
| Empty/unexpected tool list | Compare with the seven-tool DEC-030 allowlist and correct server/interpreter; never register blocked candidates to make a demo work |
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

The coordinator checks imports/syntax without configuration reads, pins,
public scope/links, baseline preservation and actual stdio with synthetic
loader and external HTTP sends forbidden. Preserve Windows event-loop
socketpair setup. Require initialize/tools-list replies with exactly seven
approved tools and no synthetic secret/origin or raw diagnostic content.
The generic SDK-client test additionally executes tools/call on synthetic
HTTP, preserving source values and observing completed cleanup. Malformed
protocol, strict input and cancellation scenarios must remain safe.

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
At this historical S5.01 checkpoint, tools, login, ongoing calls and
Sprint 6 were not released by that result. The subsequent explicit
Sprint 6 authorization and scoped G0/G1 review are recorded above and
in PRD DEC-023; they do not widen S5.01's observed facts.

## Sprint 6 verification — 2026-10-29

Scope: the approved [local-search design](superpowers/specs/2026-10-29-sprint-6-design.md)
and [implementation plan](superpowers/plans/2026-10-29-sprint-6.md).
The application entry is `await tools.search_products(client, query,
max_results=20)` with a trusted process-owned client. It is not registered
in MCP; discovery remains empty and startup still makes no ERP request.
The contract and per-operation gate evidence are in the API inventory.

The collector gained an optional strict per-call budget without changing
shared state or defaults for existing callers. The application validates
query/limit before HTTP, filters description/mask/SKU locally and preserves
partial/error semantics and normalized precision. No production change to
config.py, catalog.py, server.py or requirements.txt was needed.

| Executed check | Observed result |
|---|---|
| Task 1 TDD: focused client suite before/after optional budget | RED: unsupported max_results; GREEN: 35 tests; full suite 59 PASS |
| Task 1 independent spec/quality review | PASS / PASS; no findings |
| Task 2 TDD: search suite before/after function | RED: 15 missing-function assertions; final GREEN: 15 tests |
| Task 2 independent spec/quality review | PASS / PASS; one non-blocking weak NBSP assertion |
| Whole-change independent review | PASS for Sprint 6; no Critical/Important; two Minors: NBSP assertion and historical-checkpoint wording |
| Controller: `.venv/Scripts/python.exe -B -m unittest discover -s tests -v` | 74 tests PASS in 5.821s |
| Controller: `.venv/Scripts/python.exe -m pip check` | No broken requirements found; no installation performed |
| Post-review targeted search suite | 15 PASS in 0.182s after asserting NBSP found/count/item |
| Controller post-fix full suite, pip check and scope audit | 74 PASS in 4.857s; dependencies, scope, compilation, imports and links accepted |

Task 2's first post-implementation test run exposed fixture assumptions:
a one-row response with fixed page size 20 does not allow another page
when fewer than 20 budget rows remain. The error-path fixtures now use
budget 100, while the configuration-cap case isolates max_pages=1. The
production pagination rules were not loosened to satisfy those fixtures.

Real command: `.venv/Scripts/python.exe -B <managed-scratch>/netone_s6_real.py`.
Started at 17:25:28 UTC. The loader read private configuration in memory,
without displaying or modifying the file. Two application POSTs went to
`/app-web/api/v2/produto/reduzidos`, each JSON page=1/limit=1; both returned
HTTP 200. The first discovered a term in memory; the second used the actual
public search function with max_results=1. They were independent planned
queries, not an automatic retry. Existing guards remained installed; the
probe added a stricter two-send/page1/limit1 observation hook only.

Observed function output: pages_fetched=1, rows_received=1,
returned_count=1, status=partial, partial=true, complete_dataset=false,
error=null, local_text_search present and JSON serialization accepted.
Identity matched the first sample in memory. Response and client cleanup
completed. No source term, IDs, values, descriptions, origin, credentials,
raw upstream error or response was retained in repository/scratch output.
There was no login, token regeneration, redirect, retry or TLS bypass.

Limits: no real multi-page traversal, negative result, permission failure,
timeout, rate limit or snapshot consistency test was attempted. Offline
regressions cover bounded pagination and error/empty/partial distinctions;
they do not become remote evidence. Even a completed endpoint traversal
remains subject to provider ecommerce/price-table visibility. Task and
whole-change reviews passed; Minors corrected: the NBSP testcase now
requires a matching item, and the prior 51-test checkpoint is explicitly
historical in the PRD. Controller inspected the fixes and reran all 74
tests, pip check and the public audit successfully. No Critical/Important
or deferred Minor remains. Sprint 6 is accepted; later sprints remain
untouched and V1/operator readiness remains NOT_READY.

## Sprint 7 verification — 2026-10-29

Approved [design](superpowers/specs/2026-10-29-sprint-7-design.md) and
[plan](superpowers/plans/2026-10-29-sprint-7.md). Only client.py, tools.py
and their tests changed application behavior; the final review also led
to a test-only stdio helper correction in tests/test_server.py, with no
server/SDK change. config/catalog/server, other test modules and direct
pins remain unchanged. No install, Git, persistence or MCP registration.

| Executed check | Observed result |
|---|---|
| Task 1 TDD client suite | RED: unsupported product_id keyword; GREEN 46; full 85 PASS in 4.803s |
| Task 1 independent compliance / quality review | PASS / PASS; no findings |
| Task 2 TDD tools suite | RED: missing-function assertions; final focused 27 PASS; full 97 PASS in 5.351s before linewraps, focused 27 PASS after |
| Task 2 independent compliance / quality review | PASS / PASS; no findings |
| Controller `.venv/Scripts/python.exe -B -m unittest discover -s tests -v` | First run: 97 tests, one existing malformed-stdio recovery failure at tests/test_server.py:99; repeated full run: 97 PASS in 4.948s |
| Controller `.venv/Scripts/python.exe -m pip check` | No broken requirements found |
| Public-snapshot scope/import/compile/link audit | PASS; only Sprint 7 task states changed; unchanged lifecycle/config/normalization/pins; silent imports without .env/HTTP construction |
| Final-review M1 stdio regression | RED: five tests, missing reply ID2; corrected helper GREEN five PASS in 1.697s; worker full98 PASS in 5.572s |
| Controller post-fix full suite, pip check and public audit | 98 PASS in 5.603s; dependencies/scope/imports/compilation/links accepted |

The failed stdio run lacked the tools/list reply after malformed initialize
in the existing all-messages-then-EOF subprocess harness. A focused
synthetic repeat returned IDs99/1/2, exit0 and sanitized stderr, and the
complete suite then passed. No causal diagnosis or production correction
was established; this is an intermittent verification limitation, not
uniform success. Final review confirmed the EOF race mechanism with a
controlled delayed-handler experiment; the original event's exact cause
remains unproved. M1 led to a test-only bounded bidirectional helper:
await error/initialize/tools-list replies before EOF, drain stderr
concurrently and reap/close worker resources on failure. The delayed
handler is regression scheduling, not a parent sleep/retry workaround.
Scoped independent re-review accepted M1 as addressed, with no new
breakage. The controller independently passed all 98 tests in 5.603s,
pip check and public audit after this fix. Task 2's first GREEN
attempt also exposed a fixture expectation: an empty nonterminal page
stops for no progress before page-limit exhaustion. The fixture changed
to an advancing row; collection behavior was not weakened.

Real command: `.venv/Scripts/python.exe -B <managed-scratch>/netone_s7_real.py`.
Started 18:03:27 UTC. A persisted start marker prevents automatic rerun.
Private loader/token used in memory, no login or environment-file change.
Extra observation hooks preserved the original guard and enforced one
send per phase, products-only route, page1/limit1 and at most four sends.
Three were actually sent, all HTTP200: discovery, public details with
idsProdutos, public EAN lookup. Details: one matching reduced record,
found, partial=false, complete_dataset=true within that filtered query.
EAN: one exact match, partial=true, complete_dataset=false and fixed
local_exact_ean_search warning. Both retained the discovery identity,
had error=null and serialized correctly. Response/client cleanup completed.
Only safe counts/statuses/invariants were retained, no private values,
source timestamps, responses, origin or credentials.

The discovery sample had no usable SKU; search_product_by_sku was skipped.
No product-mask substitution, made-up term or extra discovery was used.
S7.11 remains open for real SKU validation. Additional discovery requires
a new narrowly scoped authorization, not reuse of an unspent conditional
call. No real multi-page filtered traversal, SKU variant, negative lookup,
permission error, timeout, snapshot or broad availability was tested.
Final whole-change review passed with M1, then its scoped re-review
accepted the correction without new findings. No review item is deferred.
Only S7.11's real SKU evidence prevents full Sprint 7 acceptance; the
engineering implementation is accepted. No Sprint 8+ was started.

## Commercial product-code verification — PRD 1.5.0

Maintainer approved direct implementation plus up to two filtered product
queries, at most20 rows each, without intermediate check-ins. Prefer
search_product_by_code when the operator says product code/business SKU;
do not confuse this with technical codigoSku. The approved design/plan is
[commercial-code lookup](superpowers/plans/2026-10-29-commercial-code.md).

TDD: the new focused suite first ran ten tests with expected missing-mask
keyword/function failures (RED). After implementation, all ten passed.
The complete suite passed 108 tests in 5.991s; pip check reported no broken
requirements. Public audit confirmed unchanged sprint tasks, allowed file
scope, compilation/79-column style, local links and silent imports without
configuration access or HTTP construction. Existing text/technical-SKU/
EAN/ID behavior is covered by the full regression suite.

At 18:41:47 UTC, a one-shot managed-scratch probe issued two guarded
products requests with mascara, page1/limit20. Both returned HTTP200.
Field comparison confirmed the supplied code equals mascara, not
codigoSku/idProduto/idReduzido; technical SKU was null/absent in the sample.
The actual public function returned one exact match, found, error=null,
partial=false and complete_dataset=true within the filtered traversal.
Response/client cleanup completed. No login, token rotation, retries,
redirects, guard removal or environment-file modification occurred.

Only sanitized counts/statuses/invariants are retained; the requested
commercial result was shown to the operator, not saved in the project.
No new request budget remains. The check does not complete S7.11 for
technical SKU by substituting mascara. Independent final review accepted
the implementation without Critical/Important findings. Its sole Minor
was an outdated capability-summary omission of mascara; the DEC-026
documentation update corrects that summary, without another ERP request.

## Product-field profile and priority — PRD 1.6.0

The maintainer chose up to 100 products, no raw source values retained,
then asked to continue implementation/testing offline while away. See the
[inventory and explicit limits](product-field-priority.md) and
[inline plan](superpowers/plans/2026-10-29-product-field-priority.md).

Actual one-shot command: `.venv/Scripts/python.exe -B
<managed-scratch>/netone_field_profile.py`. Started 18:52:18 UTC; two
products POSTs page1/2, limit50, HTTP200 each; 100 received rows profiled,
known projection accepted, response/client cleanup completed. No real
configuration or raw product data was written/displayed. Only known field
names, type labels and aggregates survive. Prefix sample, not full catalog.

Checked 39 known names; 36 observed, 30 populated at least once, 28 populated
in every row. EAN 93/100, observation 1/100, codigoSku null 100/100. Six
extra names were discarded; only their existence count survives. At this
initial checkpoint, the follow-up question was unanswered and no request
was executed or silently renewed while the operator was away. A later
explicit authorization and its completed one-row check are recorded below.

New tests in tests/test_product_fields.py ran RED before catalog changes:
8 methods, 43 failures including subtests (missing projections/order/type
checks). Focused GREEN: 8 PASS in 0.036s. Full command
`.venv/Scripts/python.exe -B -m unittest discover -s tests -v` passed 116
tests in 5.680s; `.venv/Scripts/python.exe -m pip check` found no broken
requirements. Tests use synthetic settings/MockTransport, no real env or
ERP; no dependencies installed. The existing source projection now adds
five optional typed fields and populated-first presentation, not matching
changes, new routes, price/stock joins or commercial inference.

S7.11 still requires an actual usable codigoSku and exact-function proof.
Null samples/mocks cannot close it, so all sprint checkboxes remain intact.
At that checkpoint, six extras were unnamed and a planned AGENTS.md update
had hit a protected-file approval timeout; the target was left unchanged,
without an alternative write path. Both approvals were later explicitly
renewed and carried out through the ordinary mechanisms below. PRD and field
contract carry the new decisions. Independent final field-priority review
accepted the narrow projection/presentation change with no Critical,
Important or Minor findings. It independently checked all 39 inventory
rows, exact optional-field additions and unchanged transport/matching/
configuration/protected instructions. Its evidence limits remain explicit:
no replay of ERP, no universal provider/stock/price guarantee, no technical
SKU acceptance or classification of the six discarded extra names.

## Approved extra-field follow-up and instruction reconciliation

The operator later explicitly approved one additional products query,
page1/limit1, retaining only names/types/presence states, and the narrow
protected AGENTS.md update to match PRD1.6.0 while preserving S7.11.
The protected patch subsequently succeeded through the normal tool;
the earlier timeout is historical, not a current pending approval.

Actual one-shot command: `.venv/Scripts/python.exe -B
<managed-scratch>/netone_extra_fields.py`. Started20:56:08 UTC,
one guarded POST products page1/limit1, HTTP200, one row. The current
projection accepted it; response/client cleanup completed. The extra
metadata is listed in [the field inventory](product-field-priority.md).
Two extras were filled: integer quantidadePecasPorEmbalagem and string
unidadeDeMedidaSigla. Four promotional fields were null; no non-null
types, final prices, units/conversion or stock facts were inferred.

Only names/types/states were retained; no source values, raw rows, private
origin, credentials, settings or upstream error text. No login/token/env
changes, retries, redirects, guard removal, new DTO/HTTP consumers or
sprint-checkbox changes. The one-request budget is consumed and closed.
The six names are observed in this new row; lost original names cannot
prove their identity/frequency in the earlier 100-row sample. S7.11 still
requires a usable technical codigoSku and real exact-function validation.

Post-follow-up verification: the complete offline unittest suite passed
116 tests in 5.658s. The public-baseline audit confirmed only the six
authorized documentation files changed, with production/tests unchanged,
all PRD checkboxes identical and all 212 sprint tasks preserved. It checked
the six new metadata rows against the actual one-row safe report and all
39 older matrix rows against the original 100-row aggregate. Compilation,
local links and silent imports without env/HTTP construction also passed.

## Sprint 7 closure by explicit acceptance with exception — PRD 1.7.0

After reviewing the real product-search result, the maintainer explicitly
selected closure with the documented technical-SKU exception. DEC-027
preserves the original S7.11 wording/open status as history and revises
only that criterion to record the available manual observations plus the
accepted exception. Marking revised S7.11 complete does not assert an
unperformed real codigoSku match, mask equivalence or full operational
coverage. The SKU function retains offline coverage and no real validation.

The additional actual search used search_products: two page1/2 limit50
HTTP200 requests, 100 received rows, eight matches, partial=true,
complete_dataset=false, error=null and completed client cleanup. The
operator reviewed the displayed results; no source values were persisted.
This search budget is also closed, not permission for a rerun or discovery.

Current controller regression: `.venv/Scripts/python.exe -B -m unittest
discover -s tests -v` passed 116 tests in 5.815s. Closure changes only
documentation, not application behavior or tests. Sprint 8 remains
unstarted, MCP registry empty and V1 NOT_READY. Any later real SKU check
requires its own usable input and bounded authorization.

## Sprint 8 execution and closed observation — PRD 1.8.0

Approved [design](superpowers/specs/2026-10-29-sprint-8-design.md) and
[plan](superpowers/plans/2026-10-29-sprint-8.md). Current workspace used
without Git/worktree helpers under the explicit project restriction;
allowlisted public-source snapshots/diffs and a managed-scratch ledger
provided scope tracking. Baseline123 tests PASS/6.441s, Python3.14.3 and
pip check PASS. Earlier116 counts predate expanded-search tests.

Production changed only client.py (per-call page ceiling) and tools.py
(price/inventory/list application consumers). Tests added16 methods in
test_sprint8.py. config/catalog/server/manifest and earlier tests stayed
unchanged. No installation, new dependency, persistence or MCP tool.

TDD: page-cap keyword absent before implementation; price5, inventory4
and list5 missing-function failures were observed before each consumer.
Focused16 tests then passed, full139 PASS/6.032s and pip check PASS.
Independent read-only review passed the application and independently
ran139 tests/5.999s. It found three Important issues only in the prepared
probe: discarded failure metrics, mandatory-match assumption on a changing
sample and insufficient same-response precision/presence validation.
All were fixed before any ERP send. Four synthetic scratch regressions
first failed (including missing expected evidence), then passed/0.042s;
the full project suite passed139/6.014s and pip check again. Fixes retain
metrics before failure, continue valid misses without replay and compare
the projection plus raw numeric/null/absence against the same consumer
response held only in memory. No Important finding remains open.

Real command: `.venv/Scripts/python.exe -B <managed-scratch>/probe.py`.
Started2026-10-29T23:25:50 UTC, finished23:26:01 UTC. A permanent exclusive
start marker forbids replay; the original request guard remained first,
with an additional phase/path/page1/limit1/five-send restriction. Existing
TLS, identity, body-size/deadline caps and zero retries/redirects retained.
Private configuration loaded once in memory, never displayed or modified.

| Phase | Requests | HTTP status | Observed public result |
|---|---|---|---|
| prices discovery + get_product_price | 2, each page1/limit1 | 200,200 | 1 exact local match, partial, error null |
| stock discovery + check_inventory | 2, each page1/limit1 | 200,200 | 1 exact local match, partial, error null |
| list_products | 1, page1/limit1 | 200 | 1 item, partial, error null |

Total5 attempts/5 received rows; each consumer pages_fetched1,
rows_received1, returned_count1, partial=true, complete_dataset=false.
Source projection/numeric strings/null/absence and JSON accepted. Currency
BRL source operator_confirmation and unknown-deposit scope accepted.
Five response aclose calls completed, as did the underlying client close;
these completion markers are stronger than is_closed alone. The sanitized
report was read back and its counts/invariants checked programmatically.
No IDs, amounts, quantities, descriptions, raw timestamps, private origin,
credentials, settings, responses or unknown keys were persisted.

Budget consumed and closed. No ERP mutation operation, login, token
rotation, env-file modification, retry, redirect or extra discovery.
No guarantee about undisclosed server internals, broader permissions,
multi-page remote traversal, stable snapshot, deposit identity, units,
freshness or stock availability is inferred. Synthetic tests cover the
additional boundaries, not real ERP behavior. S8.01–S8.15 completed within
this scope; technical SKU exception unchanged, V1 NOT_READY, registry empty
and Sprint9 not started. The managed-scratch budget marker/evidence is
retained instead of deleting the ledger because no Git history was created.

Final controller verification after the real observation and reconciliation:
`.venv/Scripts/python.exe -B -m unittest discover -s tests -v` passed139
tests in5.996s; `.venv/Scripts/python.exe -m pip check` reported no broken
requirements. The public-only audit parsed212 ordered PRD tasks: exactly15
S8 states changed, all task texts/IDs/order and non-sprint acceptance
checkboxes preserved. Foundation modules/direct pins and prior tests are
byte-for-text identical to the public baseline; Python syntax/new-line
lengths, current-document links and the real report invariants passed.
Two pre-existing long lines in tools.py were left untouched. No configured
external linter, clean install or other-platform validation was claimed.

## Sprint 9 — offline MCP integration (PRD 1.9.0)

Historical checkpoint before DEC-031's separately authorized real MCP
acceptance below. Open S9.12/G3 statements in this section record that
earlier state, not the current operational result.

Approved [design](superpowers/specs/2026-10-29-sprint-9-design.md) and
[plan](superpowers/plans/2026-10-29-sprint-9.md), executed inline in the
current workspace without Git helpers. A public-only baseline and ledger
are retained in managed scratch. No real .env read/write, ERP call,
login/rotation, installation, new filter/route or Sprint10 was performed.

The official versioned SDK README was read in the browser after extraction
failed (search-only backend):
https://github.com/modelcontextprotocol/python-sdk/tree/v1.30.0 . It states
v1.x remains maintained for critical/security fixes; v2 is the stable major.
Installed mcp1.30.0 FastMCP.list_tools/call_tool, Context.request_context,
CallToolResult, ClientSession/stdio_client and lifecycle APIs were inspected
and exercised. Existing pins are retained, not assumed latest/clean-installed.

Production changes: server.py instantiates NetOneMCP from mcp_tools.py;
config.py/client.py/catalog.py/tools.py/requirements.txt are unchanged.
Public tool hooks use the explicit seven-entry registry and strict
Pydantic models instead of SDK argument preprocessing/error echo. Error
content is fixed; application payloads preserve Decimal strings, null,
counts, warnings, status and partiality. No currency/model config input.

| Executed check | Result and scope |
|---|---|
| Baseline full unittest |139 PASS/6.067s; offline only |
| New MCP memory-session tests before implementation | RED: missing registry/consumers and unknown-tool name echo;7 methods,8 failures/5 exception-group errors |
| Initial focused GREEN |7 PASS/0.622s; all seven real application consumers over synthetic guarded HTTP |
| Existing server tests after registry change |3 expected empty-registry assertion failures; expectations reconciled to exact seven-tool allowlist |
| Initial integrated GREEN |147 PASS/7.602s, including generic SDK stdio execution |
| Additional schema/cancellation checks | Initial cancellation timeout: cancelling local SDK task alone sends no protocol notification; source inspection confirmed this. Fixture sends explicit notifications/cancelled, then response cleanup completes. No production change |
| Focused MCP tests |10 PASS/1.366s; strict types/extras, exact codes, initial/later errors, discovery/schema limits, protocol cancellation, stdio execution/cleanup |
| Full pre-review suite |149 PASS/7.567s |
| `.venv/Scripts/python.exe -m pip check` |No broken requirements found; no environment change |

The generic SDK stdio test executes initialize/list/call with synthetic
settings, blocked real .env access and external HTTP sends, no LLM keys
or LangChain/LangGraph. Invalid extras/types produce no send. One valid
listing returns a synthetic exact large Decimal, zero quantity and null
EAN, with structured/text agreement. Fixture observes one request, one
completed response close and one completed transport/client close. Raw
stdio tests also preserve malformed initialize recovery and delayed-handler
EOF regression, clean stdout and safe DEBUG stderr.

Editor diagnostics were inconsistent with the inspected pinned APIs
(snake_case/v2-style suggestions versus camelCase/v1). The editor's actual
interpreter was not checked. Root-.venv uses inspected mcp1.30.0 and passes.
No editor
configuration or alternate environment was changed; no external type-check
pass is claimed.

S9.01–S9.11/S9.13–S9.14 have offline evidence; S9.12 remains open because
no real query through an authorized MCP client was allowed or performed.
G3 offline PASS, operational PENDING. To finish that acceptance requires
a separately approved numeric request/row budget and memory-only loader
access, not reuse of earlier budgets. SKU technical/expanded search remain
unregistered; V1 NOT_READY and Sprint9 not declared complete.

### Independent review and final scope audit

The independent read-only reviewer ran149 tests PASS/7.895s, compared the
public baseline and confirmed212 ordered PRD tasks, with only the13
approved S9 states changed. No Critical or Important findings.

One Minor is deferred: mcp_tools.py's broad ValueError handler can label
an internal ValueError as invalid_arguments, while an incompatible listing
page_size/effective row budget raises BlockedOperationError and becomes
tool_error. The coordinator reproduced both through an MCP memory session:
zero sends, both isError=true, fixed safe messages and no sentinel leak.
This affects error-code diagnosis, not rejection/read-only/data fidelity.
Exact code-classification regressions and a narrower validation boundary
remain a known follow-up; this is not described as corrected.

The reviewer did not certify real configuration/credentials/DNS/TLS/token,
ERP/MCP operational acceptance or internal effects, broad pagination/
snapshot/coverage/deposit/currency/availability, SKU/expanded-search real
acceptance, upstream maintenance independently, SDK-v2 migration/static
typing, clean install/other platforms, Git or Sprint10/V1. These are
deliberately unclaimed boundaries, not additional authorization or newly
invented prerequisites for this offline delivery.

Final controller full suite:149 PASS/8.651s; pip check reported no broken
requirements. Public-baseline audit passed:13/14 S9 tasks marked, only
S9.12 open; all212 IDs/order/texts preserved, unrelated task states and
non-sprint acceptance checkboxes identical. Core application/pins and
immutable history unchanged; allowed-source syntax, new production/test
79-column style, current links and silent imports without configuration
reads or HTTP construction passed. No external linter/type-check result,
Git cleanliness, secret-file checksum or operational success is inferred.

## S9.12 — successful one-shot real MCP acceptance (PRD 1.9.1)

The maintainer explicitly approved the previously proposed minimum: one
list_products query via a generic MCP client, one page and at most one
record, using existing configuration through load_config only in memory.
No login, token renewal, environment-file write, mutation request, Git,
persistent Hermes connection or Sprint10 was authorized.

Command: `.venv/Scripts/python.exe -B <managed-scratch>/s9_probe.py`.
Before the real attempt, the same probe ran three synthetic cases: normal
success PASS; deliberately corrupted monetary projection correctly FAIL;
HTTP500 correctly FAIL while retaining attempt/status/error/cleanup counts.
The project suite passed149 tests/7.340s. An exclusive s9-real.started
marker was created before launch; it remains and prevents replay.

Started2026-10-30T01:47:59.198618Z, finished01:48:00.168265Z. ClientSession
with stdio_client initialized the actual server, discovered exactly seven
approved tools and called list_products once with max_results=1,
page_size=1, max_pages=1. The original request guard remained first; an
additional probe guard enforced only POST /app-web/api/v2/produto/reduzidos
with exactly page1/limit1 and at most one attempt. No discovery ERP request.

Observed: one guarded attempt, HTTP200, one row received and one item
returned, pages_fetched1, partial=true, status=partial, error=null,
complete_dataset=false. The limit correctly prevents a completeness claim.
Exact normalized projection, Decimal strings, null/absent fields and
missing-field metadata were compared in memory against the same consumer
response. StructuredContent and JSON text agreed across the MCP boundary.
One response aclose, one underlying transport aclose and one client aclose
completed; no closed-state-only inference. TLS/identity/byte/time bounds,
zero retries/redirects and the original application functions remained.

The safe report was read back and its counts/invariants verified. Only
fixed statuses, timestamps of the test, counts and booleans were retained;
no IDs, product descriptions/codes, monetary/stock values, source timestamps,
private origins, credentials/settings, raw response or arbitrary keys.
The report and permanent one-shot marker are retained in managed scratch,
not raw ERP data. No .env write, login, rotation or mutation operation.

S9.12 marked complete; all14 Sprint9 tasks are now accepted. G3 PASS for
seven-tool discovery and this real listing through generic MCP, not every
tool's real MCP execution or broad operational availability. V1 remains
NOT_READY; technical SKU and expanded search stay excluded. The known
Minor diagnostic-classification issue remains deferred/non-blocking.
This one-request budget is consumed and closed. No rerun, ongoing queries,
new configuration read or Sprint10 follows from this successful result.

Post-observation controller verification: full149 tests PASS/7.294s;
pip check: no broken requirements found. Closure audit PASS:212 task IDs/
texts/order preserved, only S9.12 newly marked relative to the pre-closure
snapshot,14/14 S9 tasks complete; all unrelated task states and global
acceptance checkboxes unchanged. Core application/pins/history and new
runtime/test sources match their reviewed public snapshots; current local
links and every safe real-report invariant passed. No further ERP send.
