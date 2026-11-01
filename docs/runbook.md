# Operations and verification runbook

## Current boundary

PRD1.15.0 / DEC-038 records the directed commercial-query fix,229 offline tests
and two separately authorized real filtered checks, both HTTP200/one matching
row/nonpartial with source fidelity/JSON/completed cleanup accepted. One loader
invocation and the new two-attempt budget are consumed/closed; no query/read
permission remains. AGENTS.md was reconciled after explicit resubmission and
normal protected approval. Prior campaign permissions below are historical,
not active here. Eight tools, existing
sprint/global checkboxes and V1 NOT_READY/G6 pending remain unchanged.

PRD1.14.0 / DEC-037 was the previous approved extension: resumable catalog
blocks plus list_inventory (eight tools), with the original seven defaults
and the same guarded three-query HTTP contract. Only an external consumer
associates catalog/stock in memory. Execution plan:
[resumable inventory](superpowers/plans/2026-10-31-resumable-inventory.md).
The new authorized campaign is capped at1200 products/stock attempts,
limit<=50 and45 minutes, including validation; no retry/redirect/login,
.env mutation, install, Git, publication or business write. Runtime and
budget evidence will be recorded below after execution; no result is
claimed in advance. V1 NOT_READY/G6 pending and all existing checkboxes
remain unchanged. The next paragraph is the historical Sprint13 boundary.

PRD1.13.0 / DEC-036 records twenty evidenced Sprint13 tasks; independent
review found no Critical/Important issue. G6/global acceptance remains pending.
The later separate installation/temporary-env/private-read/one-query consents were
exercised: clean-install195 PASS, one MCP products listing HTTP200/one partial
item with fidelity/JSON/cleanup accepted. Real read/query budget is CLOSED;
no repeat, login/rotation, .env write, Git or publication is authorized.
Seven tools, bounded G3/G4, G6 pending and V1 NOT_READY remain.
Current execution evidence is in the Sprint13 ledger at the end of this file.

The following boundary describes the historical Sprints12/14 checkpoint:
PRD1.12.0 / DEC-035 authorizes only Sprints12/14 documentation and controlled
handoff, with the approved design and continuous execution through review.
Sprint13 is not executed or marked; V1 stays NOT_READY and G6 pending.
MCP remains exactly seven tools, literal search only. Technical SKU, expanded
lexical search and deterministic analyses are application-only. Remote
price/stock filters remain plans, not implementation.

DEC-031 records the one authorized real MCP listing: page1/limit1, HTTP200,
one partial item, completed response/transport/client cleanup. G3 remains
limited to that evidence. DEC-033/G4 covers synthetic application analyses;
DEC-034 records offline security/quality review, not new ERP proof.
All real configuration-read/query budgets remain closed. No real .env
access/write, ERP query, login, rotation, Git, installation or publication
is part of the current work. BRL is historical operator-confirmed application
context, never a generic MCP currency or API-returned field.

Earlier sprint sections below preserve their original default values, test
counts, registry states and authorization boundaries as dated history. They
are not current instructions, renewed budgets or a substitute for Sprint13.
Current contracts: [README](../README.md), [architecture](architecture.md),
[security](security.md) and the [current API matrix](api-capabilities.md#current-implementation-matrix).

Current behavior and limits: [configuration](configuration.md). Endpoint contracts, field mapping and unresolved provider ambiguities: [API inventory](api-capabilities.md). Canonical sprint IDs/states/sequence: [PRD section 28](../PRD.md#28-sprints-de-implementação-em-checklist).

## Directed commercial-query fix — DEC-038

### Cause, decision and boundaries

check_inventory and get_product_price called _collect with page/limit only,
then selected exact textual identity locally. max_results bounds received
rows, not target matches: the default20-row budget can stop after page1
despite a large totalPages. This was accurate partial reporting, but an
inefficient lookup design for an identity that has a documented remote filter.
Increasing caps or scanning the entire endpoint is not the chosen fix.

Changes reuse client.py/tools.py/mcp_tools.py and existing test fixtures.
No new route, tool, dependency, cache, join, deposit choice or environment
setting. Prices uses idsProdutos singleton numeric array; stock provisionally
uses idsReduzidos singleton numeric array. Each filtered page is identity-checked
atomically, budgets stay isolated/fixed and no error triggers replay, scalar
attempt or unfiltered fallback. All transport, sanitization and cleanup
controls remain. Source fields/Decimal/null/absence/zero are unchanged.

Ruling: stock array follows the official operation example and linked official
Postman collection, despite number in the OpenAPI schema. The conflict remains
unresolved by the supplier, not merely a rendering error. The delegated offline
implementation supersedes the former project refusal narrowly; if this choice
is wrong, a future authorized call should fail safely without alternate sends,
and the supplier must clarify it. This is not remote acceptance.

Ruling: preserve noncanonical textual IDs with the existing bounded local
exact lookup and explicit lookup_strategy=bounded_local_exact plus
numeric_id_filter_unavailable. Do not silently convert leading zeros, signs,
Unicode digits or significant spaces to another identity. Canonical ASCII
numeric IDs within0–9223372036854775807 use remote_id_filter; canonical overflow
fails pre-send. Cost: legacy textual identities remain subject to prefix caps.

Ruling: work in the existing checkout without Git/worktree/commit helpers,
as required by project policy. An allowlisted public snapshot in managed
scratch provides comparison without reading .env/.git or replacing prior edits.

Official sources and unresolved-contract details are in
[the current inventory](api-capabilities.md#directed-identity-queries--dec-038).
Only public documentation GETs/browser reads were made, never Send/Try or
queries to the documentation's ERP test host. The public Postman collection
returned HTTP200; both relevant saved-response arrays are empty. There was
no real NetOne send, private loader invocation, .env read/write, installation,
login/rotation, Git, publication or Hermes-registration change.

### Executed verification

- Existing .venv interpreter: Python3.14.3. Baseline:
  `.venv/Scripts/python.exe -B -m unittest discover -s tests -v`:
  214 PASS/9.139s.
- RED before implementation: seven new directed-consumer tests failed on
  missing body filters/lookup_strategy and wrong found/partial/error behavior;
  the requested product-code fixture reproduced partial instead of found.
  Three low-level filter tests also failed before the private argument/admission
  existed. Tests use the supplied identifiers and simulated values only.
- Focused consumers/client after implementation:71 PASS/3.774s.
- Intermediate whole-suite run:223 tests, one expected legacy MCP body
  assertion failed because prices now sends idsProdutos; updated that specific
  expectation. No unrelated failures were hidden.
- The new directed stdio test failed before its synthetic fixture supported
  stock/prices, then passed with strict body assertions and external sends
  forbidden. Both calls observe response closure and one client/transport close.
- Whole suite after implementation/MCP fixture:
  `.venv/Scripts/python.exe -B -m unittest discover -s tests -v`:
  228 PASS/9.777s. Tests include the reported985-page-prefix miss, closed bodies,
  IDs/bounds/invalid arguments before send, zero/null/absence, terminal empty,
  wrong/missing/mixed identities, later-page rejection/errors, caps/conflicts/
  missing metadata, source tables/precision, concurrent IDs/budgets, cancellation
  with completed cleanup, generic MCP stdio and unchanged registry/defaults.
- `.venv/Scripts/python.exe -B -m pip check`: No broken requirements found.
  No installation or dependency change was performed.

### Independent review and verified fix pass

Independent read-only review ran228 tests PASS/10.105s and pip check PASS,
compared the26-file public snapshot, unchanged public signatures and checklists.
No Critical finding; one Important pre-existing stock-conflict defect (I1),
one pre-existing Minor documentation inconsistency (M1).

I1: conflict grouping used (product_id,reduced_id), although stock identity is
reduced_id and product_id is optional. Two incompatible quantities for one
reduced ID could appear found/complete when product_id differed or was absent.
The coordinator reproduced this in a new transport-backed regression, with
nine failing subcases across check_inventory, list_inventory and analyze_inventory.
The fix changes only stock grouping to reduced_id, preserving both rows,
conflicting_rows_preserved and partiality without summation; products/prices
retain their original grouping. Regression GREEN/0.032s, whole suite229
PASS/10.116s after the fix. This is a verified implementer fix pass, not a
claim that the independent reviewer reran the corrected revision.

Final coordinator verification on the corrected tree:
`.venv/Scripts/python.exe -B -m unittest discover -s tests -v`:
229 PASS/10.279s, exit0, with229 individual OK lines counted;
`.venv/Scripts/python.exe -B -m pip check`: No broken requirements found.
The final snapshot/checklist/parser/new-line-length audit also passed.
The existing checkout is preserved without any Git operation or integration.

Final: minor (deferred): M1, PRD.md's legacy status paragraph at line4 still
mentions seven tools; the current DEC-038 section, registry and discovery
tests explicitly establish eight. This pre-existing header-only inconsistency
is retained for a separate documentation cleanup, not an implementation issue.

Final: Ruling on the review's declined operational judgments: server acceptance,
definitive number/array clarification and live behavior stay unverified and
pending fresh authorization; offline success cannot supply that missing proof.
No new call was made to settle them.

Final public audit:256 PRD checklist lines exactly match the pre-edit snapshot;
AGENTS.md, requirements.txt and catalog.py are unchanged;18 Python files parse;
no new over79-character lines in modified Python code. All87 local links/anchors
in the seven affected documents were valid. These checks do not constitute
an index/history audit, protected configuration comparison or publication clearance.

### Subsequently authorized real validation

The maintainer explicitly requested resubmitting the protected AGENTS.md update
and then executing the previously proposed real tests. The normal protected
mechanism approved/applied that narrow update, and a readback confirmed it.
New nonrenewable scope: one load_config invocation only in server memory;
at most two guarded attempts total, one stock/check_inventory and one
prices/get_product_price, page1/limit20, using the already-supplied identities.
No discovery, extra page, retries, redirects, scalar/unfiltered fallback,
login/rotation, .env write/display, ERP mutation, Git, install, publication or
registration changes. Stop after an error, inconsistency or incomplete evidence.
Retain structural evidence only; commercial values belong only in the operator
response. A scratch one-shot marker must precede the live attempt; offline
probe checks and budget consumption/results are recorded below.

#### Executed one-shot result and closed budget

The temporary managed-scratch probe was exercised with six synthetic cases:
success, HTTP error, wrong response identity, deliberate numeric-fidelity
corruption, failure precedence after a reply and unknown quantity. All six
checks passed with no private loader invocation. The project regression also
passed229 tests/10.074s before the live run.

Actual command:
`.venv/Scripts/python.exe -B <managed-scratch>/netone_dec038_live_probe.py --live`.
An exclusive consumption marker preceded the single launch. Execution began
2026-10-31T21:39:53.889316Z and finished21:39:54.425448Z; exit0. A generic SDK
MCP session in memory initialized the actual production server factory and
discovered exactly eight tools, then called check_inventory and get_product_price
sequentially through the unchanged application/collector/guard/real HTTP path.
This was not a real stdio rerun; stdio regression remains separately offline.

- Exactly one load_config invocation, values held only in server memory.
- Exactly two guarded POST attempts: stock with idsReduzidos singleton array,
  then prices with idsProdutos singleton array, both page1/limit20.
- Both HTTP200; each accepted one fetched page, one received/returned matching
  row, status found, partial=false, error=null and complete_dataset=true only
  within its filtered query. No broad-catalog claim follows.
- Both same-response checks passed: explicit independent source-to-output
  projection including IDs, Decimal strings, null/absence/missing_fields,
  plus structured MCP/text JSON equivalence. The production normalizer was
  not used as the sole fidelity oracle.
- Two underlying response-stream close completions, one transport close and
  one client close observed after awaiting the original cleanup operations.
  No closed-state flag was used as the sole evidence.
- Original HTTPS/origin/Host/route guards, TLS, identity/1MiB, timeouts and
  zero retries/redirects remained. An additional hook after the original guard
  restricted exact bodies/phase/attempts; it did not replace the production guard.
- Commercial values were returned only to the authorized operator; no raw
  responses, credentials, origins, source descriptions or amounts were written
  to the project/report. The saved probe report contains structural evidence only.

CONSUMED/CLOSED: no remaining loader read, attempt, discovery, rerun or automatic
replay is authorized. Earlier budgets remain closed. This demonstrates that
the singleton stock array was accepted for this known identity in this
installation; the supplier's number/array documentation conflict, general
filter guarantees, freshness/deposit identity and broader coverage remain
unverified. No login/rotation, .env write, ERP mutation, Git, installation,
publication, registration change or sprint/global acceptance was performed.

After evidence/documentation reconciliation and the description-only MCP
wording update, final offline verification passed229 tests/10.833s and
pip check reported No broken requirements found. Readback of the saved
structural report confirmed the exact two attempts/one loader/cleanup counts;
all256 PRD checklist lines and direct dependency pins remain unchanged.

The pending-action list below describes the earlier pre-authorization
checkpoint, retained as history rather than an active approval gate.

### Remaining human/real validation — historical pre-authorization checkpoint

- AGENTS.md update was not applied: the protected-write approval timed out
  without response. No retry or alternate write path was used for that file.
  Its old price/stock filter instructions remain stale for DEC-038; the maintainer
  must explicitly renew approval to reconcile that narrow section. This is a
  separate instruction-file approval, not permission for real ERP queries.
- Resolve stock's number/array inconsistency with the supplier or an authorized
  controlled observation; offline results cannot settle what the server accepts.
- Separately authorize a bounded real check of both actual MCP consumers using
  the private loader only in memory, preserving the existing guard, and compare
  identity/Decimal/null/paging/cleanup against each same response. Proposed
  initial ceiling: two attempts total, one stock and one prices, page1/limit20,
  no discovery/replay/redirect/fallback; stop on error or incomplete evidence.
  This is a proposal, not authorization or a claim of execution. More than one
  filtered page, missing metadata or changing totals remains an explicit limit.
- No real quantity/price, broad coverage, filter acceptance, supplier correction,
  release, G6/global acceptance or new sprint completion is claimed.

## Sprint 10 — offline application analysis evidence

The maintainer chose application-only option1, approved the
[design](superpowers/specs/2026-10-30-sprint-10-design.md) with threshold3,
then approved the [native execution plan](superpowers/plans/2026-10-30-sprint-10.md).
Work stays in the existing checkout with a24-file allowlisted public-source
snapshot in managed scratch, not Git/worktree helpers. Production changes
are limited to tools.py and the justified new analysis.py; HTTP/configuration/
normalization/server/registry and requirements remain unchanged.

Executed `.venv/Scripts/python.exe -B -m unittest discover -s tests -v`:
baseline170 PASS/8.453s, Task1 checkpoint176 PASS/8.721s, Task2 checkpoint183
PASS/10.074s and implementation checkpoint190 PASS/8.416s. Interpreter:
the root .venv Python3.14.3, not the unrelated Python on PATH.
`.venv/Scripts/python.exe -m pip check`: `No broken requirements found.`

TDD: six pure-metric cases first failed because analysis was absent; seven
public-consumer cases first failed because functions were absent. Both sets
passed after implementation. A multi-page fixture initially incorrectly
expected a second size2 page with only1 residual row available; corrected
the fixture to budget100/size50 without changing production pagination.
An adversarial test reproduced a projected duplicate after a nonfirst
conflicting record being undercounted (0 versus1). Per-identity sets corrected
the count while still excluding the entire conflicting group; regression
passed. Other adversarial cases characterize existing protected transport.

Coverage includes threshold3/boundary Decimal/zero/negative/null/absence,
noncoercing input rejection before send, IDs with leading zeros, duplicate/
conflicting reduced identities including another product ID, classification
sentinel collision avoidance, missing/contradictory metadata, repeated pages,
initial/later HTTP401/403/404/429/500 and timeout, restrictive configured caps,
concurrent different thresholds/budgets, and cancellation of both consumers
with response stream aclose completion observed before unwind. Existing
MCP/stdio and client-cleanup tests remain green and registry stays exactly7.

Manual synthetic demonstration executed both actual public functions through
NetOneClient/guard/normalizer and an in-memory MockTransport. Fresh imports
forbade client construction, DNS and protected .env reads; execution used an
empty process environment, blocked configuration reader and synthetic Settings
only. No LLM key or provider request. One page1/limit50 stock response with5
rows returned known3/unknown2, low_stock2 at threshold3, zero1, above1;
complete_dataset=true for the fixture but metrics_complete=false because two
quantities were unknown. One page1/limit50 products response with2 reduced
variants returned one distinct product and classified description populated1/
null1. Both were found in the fixture's visible_endpoint scope. Exactly two
mock requests, two response closes, transport close completion and closed
client were observed. Synthetic fixture source remains netone_api in the
unchanged result envelope; the harness labels the observation SYNTHETIC ONLY.

No quantity/unit/deposit sums, inferred stock from products, ERP-wide metrics,
snapshot/freshness guarantees or sellability conclusions. Low stock <=3 is a
local approved analysis rule; missing quantities remain unknown. Error codes,
items/Decimal/null/zero/false/missing_fields and collection limits survive.
metrics_complete never establishes full collection; consult analysis_scope
and complete_dataset before interpreting any count beyond the sample.

Independent final review reran190 tests PASS/8.758s and pip check PASS,
then two additional in-memory adversarial cases PASS/0.031s (classification
sentinel strings with cross-product conflicts; exact IDs with zeros/case/
spaces and all quantities unknown). No Critical/Important/Minor findings.
The reviewer verified24 baseline files,226 unchanged ordered sprint tasks
at the review checkpoint and54 local file links (not anchors). No ERP/configuration read, dependency
install, login/rotation, Git or Sprint11+; all older real budgets remain closed.
S10.01–15 are complete; G4 passes only for the bounded synthetic analysis
scope. G3 and V1 are not promoted; no real analysis proof is claimed.

Final coordinator verification after documentation closure and line-length
formatting:190 tests PASS/8.653s, pip check PASS. The public-source audit
confirmed exactly15 state changes S10.01–15 (15/15 complete) among226 ordered
sprint tasks, with all task text/order and unrelated/global checkboxes
unchanged. Only the six planned existing files and four new artifacts differ
from the baseline scope; prior tests, HTTP/configuration/normalization/server/
registry and manifest remain unchanged. Syntax compilation,54 local file
links and the two new section anchors passed. No static type-checker or clean
installation claim is implied. Review boundaries retained: real ERP behavior
was not judged or queried, and historical RED/baseline/demo observations
remain the coordinator's executed evidence, not independently re-created
operational proofs. No deferred review findings.

## Sprint 9.5 — offline execution evidence

The maintainer chose option1 and approved the
[design](superpowers/specs/2026-10-29-sprint-9-5-design.md) and
[plan](superpowers/plans/2026-10-29-sprint-9-5.md). Work used the current
workspace, a public allowlisted baseline and contextual diffs in managed
scratch, not Git/worktree helpers. No private configuration file or ERP was
read; only synthetic Settings/streams were used in execution. No dependency
install, login, rotation, new route/filter/tool, or Sprint10 work.

Executed baseline command:
`.venv/Scripts/python.exe -B -m unittest discover -s tests -v`
returned149 tests PASS in7.268s. `.venv/Scripts/python.exe -B -m pip check`
returned `No broken requirements found.`

Incremental RED→GREEN evidence:

- Literal second-page fixture failed to return target before the default
  change; new output-limit/metadata cases initially failed because the input
  and fields did not exist. After implementation,31 tool tests and46 client
  tests passed. Explicit20 and restrictive configuration retain row ceilings.
- Expanded composed phrase initially omitted reviewed alternatives, accepted
  embedded words/plurals and missed accent-normalized comparison; independent
  output limit was unsupported. The focused12-test set passed after minimal
  changes, then the whole158-test checkpoint passed in8.143s.
- Serialization regression detected a redundant deepcopy of an immutable
  synthetic Decimal subclass. The regression passed after shallow field
  projection. Existing field fidelity/null/zero/false tests passed unchanged.
- MCP regressions initially failed the default schema, second-page lookup
  and compact text requirement. The focused12 MCP tests passed after input/
  description/serialization updates. Input limits remain strict/extra-forbid.
- Generic SDK stdio second-page search initially returned an error because
  the old synthetic fixture admitted only page1/limit1. Extending that fixture
  supplied two guarded page/limit responses. The actual application/server/
  SDK path then found row51, preserved exact Decimal/zero/null and observed
  two response closes plus one client close. Existing one-page listing proof
  remains a separate synthetic scenario; stdout stayed protocol-only.

Full implementation checkpoint, same unittest command:169 tests PASS in
7.996s; pip check passed. Coverage includes later errors with/without matches
and output cuts, ambiguous phrases with suggestions, LS2/LS20 and literal
metacharacters, restrictive/explicit budgets, duplicated/conflicting records,
missing/contradictory metadata, empty/repeated pages, concurrent literal/
expanded budgets and deadlines/cancellation with response cleanup completed.
Existing MCP protocol-cancellation/client-cleanup tests remain green. No
static type-checker or clean-install acceptance is implied by these results.

### Reproducible synthetic cost and remaining external work

Final independent review ran169 tests PASS in8.052s and pip check PASS;
it reproduced all synthetic cost figures and found no Critical/Important
issues under its original grading. One Unicode edge case was reported as
Minor: a combining-mark-only term normalized to empty and matched records
without textual evidence. The coordinator treated the false commercial
result as requiring correction, not deferred polish. A failing regression
covered query, required/suggested terms, an implicit phrase restriction and
an ignored suggestion in an ambiguous phrase. Validation now rejects empty
or whitespace-only lexical comparison terms before collection. The focused
RED run failed as expected; final full suite170 PASS in8.287s and pip check
PASS, followed by repeated identical cost measurements. No finding remains
deferred from this review. Static typing, clean installation and provider
behavior were not revalidated; all new evidence remains offline.

Same-universe comparison used fixed in-memory rows and counted requests,
pages, received rows, matches and compact payload bytes, not wall time:

| Consumer/scenario | Requests/pages | Rows | Matches/returned | Compact payload bytes |
|---|---|---|---|---|
| Literal explicit20, absent target in prefix | 1/1 | 20 | 0/0 | 542 |
| Literal default100, target at51 | 2/2 | 51 | 1/1 | 1046 |
| Expanded100, three deduplicated terms, same target | 2/2 | 51 | 1/1 | 1347 |
| Local price exact identity, variants/tables/conflict | 1/1 | 3 | 3/3 | 2105 |
| Local stock exact reduced identity/conflict | 1/1 | 3 | 2/2 | 1640 |

Literal/expanded100 sent identical bodies page1/limit50 and page2/limit50.
The old20-row prefix is less work and lower coverage, not an equivalent
universe for a speedup claim. Expanded provenance costs extra payload bytes;
terms do not multiply collections. Price/stock keep all matching variants
and conflicting records as partial, not first-match selection.

For50 synthetic records/two Decimal amounts each, the baseline serializer
called amount deepcopy200 times (record traversal twice); current serializer
called it0 times. All prior result values compared equal. The exact same
current result was27017 bytes with spaced JSON and24783 compact:2234 bytes/
8.27% saved in textual JSON only, excluding MCP wire-envelope overhead. Both
structuredContent/text remain; no null/field/warning was dropped. Synthetic
measurements are fixtures, not installation-specific values or ERP timing.

O5/O4 official pages were read anonymously after hydration. O5 publishes
product/reduced numeric arrays; combinations/ceilings and exact enforcement
remain unverified. O4 still publishes number versus array for idsReduzidos.
The [inventory](api-capabilities.md#o5o4-reinspection-and-future-directed-query-plan-no-filter-implemented)
records the minimal future body/test plan, lossless identifier restrictions,
owner and unblock evidence. Current price/stock remain page/limit-only local
selection. No filter implementation, real query or lexical MCP release follows
from this investigation. G3 scope/V1 NOT_READY and closed budgets unchanged.

## Evidence retained, not re-executed

[The historical runbook through PRD1.1.6](history/runbook-through-1.1.6.md)
preserves prior scenarios, PASS/FAIL/BLOCKED results, harness failures,
findings and corrections. [PRD1.1.6](history/PRD-1.1.6.md) preserves its
requirements/decisions/checklist context. These records received only the
explicitly authorized identifying-reference substitutions in Sprints12/14;
they are no longer verbatim or byte-identical. Historical decisions/results/
checklists remain, while obsolete deny-all/GET-only rules are not current
policy. Relative links retain their original-location interpretation; use
[the archive index](history/README.md) for navigation and redaction scope.

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

## Future authorized manual validation

This is a procedure for a separate owner-approved acceptance session, not an
execution of Sprint13 or permission to repeat historical probes:

1. Agree on the exact consumer, method/path/closed body, numeric attempt/page/
   row ceilings and retained structural evidence. Configuration-read consent
   is separate from query consent; old consumed budgets cannot be reused.
2. Review current loader/guard/TLS/limits offline first. The operator selects
   the intended origin and credentials privately; never diagnose by dumping
   settings or copying .env into a report. No automatic login or token rotation.
3. Use a generic SDK stdio client with the root-.venv absolute executable and
   server.py paths. Await initialize before tools/list, inspect exactly seven
   names, then send only the approved tools/call. The existing
   tests/test_mcp_stdio.py shows this sequence with synthetic settings only;
   do not replace its fixture with live configuration to run offline QA.
4. Count actual request attempts and statuses. Keep source data only in memory
   for same-response projection/Decimal/null/absence comparison. Check
   structuredContent/text JSON equivalence; retain only approved fixed codes,
   counts, booleans and sanitized observations. A valid partial miss is not
   failure of identity matching or proof of global absence.
5. Observe completed response/transport/client cleanup. Preserve cancellation
   and initial errors. A stalled bounded close, HTTP429, timeout or changing
   sample never permits a retry, extra discovery or relaxed guard.
6. Close the budget durably, record actual PASS/FAIL/BLOCKED and its scope,
   and reconcile only the acceptance tasks supported by that evidence.
   Failure paths may be exercised synthetically rather than provoking rate
   limits or permission changes in the ERP. Never invent remote error proof.

No real calls or private loader access were performed to write this procedure.

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

This paragraph is the historical Sprint 9 checkpoint. Sprint 11 below
reproduces and fixes the diagnostic classification issue offline; it does
not expand Sprint 9's real-call evidence.

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

## Sprint 11 — offline security and quality review

PRD 1.11.0 / DEC-034. The maintainer selected review with minimal verified
corrections and direct execution without intermediate approvals. The
[plan](superpowers/plans/2026-10-30-sprint-11.md) records the short design
and scope. No Git, real .env access, ERP request, login/rotation, install,
new dependency/filter/tool or Sprint 12+ work was authorized or performed.
Seven MCP tools and V1 NOT_READY remain unchanged.

### Reviewed controls and item evidence

| PRD task | Evidence and boundary |
|---|---|
| S11.01 | Reviewed client._query/_request_guard and all application consumers. Exactly POST reduzidos/precos/estoque, closed page/limit plus products-only exclusive idsProdutos or mascara; tests exercise exact bodies, invalid combinations and destination rejection before transport. Guard is not an arbitrary trusted-process body sandbox. Zero redirects/retries/fallback. |
| S11.02 | MCP discovery and execution tests cover exactly seven approved queries, strict extra-forbid inputs, no HTTP/configuration/CRUD arguments. Technical SKU, expanded search and analyses remain unregistered. |
| S11.03 | config.py is the sole explicit loader, process-owned origin/token, immutable repr-safe Settings; configuration tests mock file reads, verify override/no interpolation/no environment mutation. No real configuration was loaded. |
| S11.04 | Root/MCP/HTTPX/httpcore DEBUG diagnostics retain fixed level/component/code only; malformed stdio recovers; exception and input sentinels are absent from logs/replies. Internal ValueError classification fixed below. |
| S11.05 | .gitignore includes .env, .env.*, .venv/ and neutral-example exception. No Git/index inspection: ignore patterns do not prove that no secret was previously tracked or committed. |
| S11.06 | This execution did not read/write/move the real .env. Tests replace file reads or forbid real reads; baseline/diff inventory excludes it. Preservation is scoped to this execution, not an unperformed historical checksum or a guarantee against third-party edits. |
| S11.07 | Synthetic effective HTTPX transport inspection verified CERT_REQUIRED, hostname checking, trust_env=False, no proxy mounts despite synthetic HTTPS_PROXY/CA overrides, no redirects, identity encoding. URL tests cover HTTPS, userinfo/path/query/fragment/encoding, port, equivalent origins/private hosts. No live TLS/DNS claim. |
| S11.08 | Effective phase timeout15/total60, zero retries, pool1/keepalive1 verified offline. Existing tests cover 429/Retry-After, redirects, timeouts, bytes/compression/invalid JSON, fixed-page budgets, contradictory metadata and completed cleanup under cancellation; stalled close remains bounded failure, not release assurance. |
| S11.09 | Catalog/application/MCP tests preserve exact Decimal strings, IDs/zeros, false, absent/null/zero, distinct variants, duplicates/conflicts, partial errors; analysis tests preserve explicit metric universe and unknown quantities. No invented currency/deposit/freshness. |
| S11.10 | New protocol projection test supplies unprojected token/header/private URL/nested password sentinels: none reaches result/logs; description instruction-like text remains data and triggers no additional request. Structured/text JSON agree. Authorized commercial fields are intentionally returned, not globally redacted. |
| S11.11 | Public root/tests/docs inventory contains no Docker, DB/migrations or CI/CD implementation; manifest/source imports have no such consumer. Private .git/.venv/secret trees were excluded, not crawled. |
| S11.12 | Syntax checked in20 source/test files; direct installed pins exactly match requirements and pip check passes. PEP8-oriented manual/token/line review preserves English names, useful types and single quotes (one intentional double-quoted string contains an apostrophe). Existing long lines remain documented style debt; no external linter/type checker, clean install, vulnerability-free dependency claim or other-platform claim. |
| S11.13 | Corrected MCP error classification and stale current README registration statements. The protected AGENTS.md update initially timed out; after the maintainer explicitly requested renewed submission, the normal protected patch applied it. No bypass. Independent review/final reconciliation and the resolved timeout are recorded below. |

### Minimal correction and executed checks

Root cause: mcp_tools.call_tool caught all ValueError across application
execution and JSON serialization. An internal failure therefore looked like
invalid_arguments. Conversely, listing page_size above the effective row
budget reached the collector's BlockedOperationError and became tool_error.
Neither case bypassed rejection or leaked data, but diagnosis was inverted.

Registered consumers now raise tools.ToolInputError (ValueError subtype)
for explicit application argument rejection. MCP catches that type, not
arbitrary ValueError. Listing validates explicit page_size against both
requested and configured row ceilings before collection. Application callers
of that invalid listing now receive ToolInputError rather than the private
collector's BlockedOperationError; this intentional exception-type change
is documented in README. The collector still independently guards its own
inputs. Application-only analysis/expanded-search validators are not migrated
merely for hypothetical MCP consumers. No accepted inputs, defaults, payload
fields, commercial matching or request budgets changed.

| Command/scenario | Actual result |
|---|---|
| Root .venv interpreter | Python3.14.3, Windows |
| `.venv/Scripts/python.exe -B -m unittest discover -s tests -v` baseline |190 PASS/8.436s |
| Three new protocol classification regressions before fix | RED: three failed assertions (reported as errors via SDK ExceptionGroup),0.095s; internal and serialization errors returned wrong category, incompatible page size returned wrong category |
| Focused test_mcp_tools after fix |15 PASS/0.911s |
| First integrated run after fix |193 run/one error: existing test_list_inputs_never_send expected BlockedOperationError for page_size above configured cap; aligned to the documented application ValueError subtype |
| Added projection and real argument-validation classification checks | Existing behavior confirmed; no production change needed |
| Full suite after expectation reconciliation and added checks |195 PASS/8.404s |
| `.venv/Scripts/python.exe -m pip check` |No broken requirements found |
| Managed-scratch audit.py with synthetic Settings | PASS effective transport controls, import/config/network restrictions, pins, syntax20 files, ignore patterns and public infrastructure inventory |

Snapshot, logs and execution ledger use managed scratch netone-s11;
54 baseline files contain public source/documentation only. The audit uses
installed HTTPX private transport attributes strictly for read-only
inspection, never production writes. No settings, environment dumps or
private file contents are retained. Import checks block real .env opens,
HTTP-client construction, DNS and socket connect; transport checks create
the Windows event loop first before blocking connect, then instantiate
only a synthetic client without sends.

### Residuals and publication limits

- Resolved after renewed authorization: AGENTS.md now records Sprint11
  completion, bounded evidence, the explicit input-error contract and
  unchanged ERP/configuration/Git/Sprint12+ restrictions. The first protected
  approval timed out; the maintainer later explicitly requested renewed
  submission and the normal patch tool applied it. No bypass occurred.
  The timeout and stale status are historical, not current residuals.
- No .env checksum, Git index/history/secret scan, live token/TLS/ERP proof,
  dependency advisory audit, clean installation or platform matrix was run.
  Do not equate this bounded security review with public-release approval.
- Existing source/test long lines are retained rather than reformatted
  broadly. The baseline runbook ended at S9.12 despite later PRD references
  to Sprint9.5/10 evidence; this review revalidates their implementation in
  the current195-test suite but does not fabricate missing historical logs.
- Provider-internal side effects, broad permissions, snapshot/coverage,
  unit/deposit identity, freshness, technical SKU and O4 filter ambiguity
  keep their prior limitations. No earlier query budget is reopened.

### Independent review and final reconciliation

The independent read-only reviewer inspected all seven production modules
and the public difflib comparison; ran195 tests PASS/8.629s and pip check
PASS; reran the synthetic audit in memory without writing its report.
No Critical/Important finding or unresolved critical security deviation
was identified in this bounded scope. Two Minor findings were deferred at
that checkpoint: stale protected AGENTS.md status and preexisting lines
above79 columns. The former was subsequently resolved by an explicitly
renewed protected-edit request; only existing line-length debt remains.
No production-code fix pass was needed.

S11.01–13 are accepted within the evidence boundaries above; S11.13 records
the protected-document divergence and its later authorized resolution.
S11.06 is not historical byte verification. The final coordinator command
and checklist reconciliation are recorded after their execution below.

Final coordinator verification: `.venv/Scripts/python.exe -B -m unittest
discover -s tests -v` passed195 tests/8.643s; `.venv/Scripts/python.exe -B
-m pip check` reported no broken requirements. Public scope.py comparison
verified226 ordered task IDs/texts: only13 S11 states changed to complete;
all unrelated task states and non-task/global checkboxes unchanged. Added
Python lines fit79 columns; checked local links resolve. Seven existing
public files changed and one plan was added. config.py/client.py/catalog.py/
analysis.py/server.py, manifest, ignore/example, prior archives and protected
AGENTS.md remain identical to the public baseline. No .env read/checksum,
Git or ERP action occurred. Sprint11 is complete in this bounded offline
scope with two disclosed Minor residuals at that checkpoint; the later
protected-instruction update resolves one, leaving only existing long lines.
V1 remains NOT_READY. This follow-up changes documentation/instructions only;
the test results above are the preceding executed verification, not a new
test run or operational authorization.

## Sprints 12 and 14 — documentation and controlled handoff

Date:2026-10-31. PRD1.12.0 / DEC-035. The maintainer confirmed only Sprints12
and14, excluding13, approved the [design](superpowers/specs/2026-10-31-sprints-12-14-design.md)
after an independent builder check found no important gaps, and approved
continuous execution through final review. The [plan](superpowers/plans/2026-10-31-sprints-12-14.md)
uses native edits and one independent whole-change review. No intermediate
permission loop, production/test change, install, Git or real configuration/
ERP operation is part of this work.

### Deliverables and task evidence

The following ledger states the evidence required for checklist marking;
verification results and final acceptance follow below. It is not a second
copy of the canonical PRD checklist.

| PRD task | Deliverable / acceptance evidence and limit |
|---|---|
| S12.01 | README introduction explains bounded read-only queries, application analyses and no invented conclusions; English public prose. |
| S12.02 | README/local-dev require Python >=3.14,<4, one root .venv, create only if absent, no unauthorized replacement. |
| S12.03 | requirements.txt pins compared to installed metadata; all direct imports have consumers; existing environment only, no clean-install claim. |
| S12.04 | Configuration guide and .env.example use variable names/neutral example.invalid and empty credentials; no existing .env read/overwrite. |
| S12.05 | README command/args example with absolute-path placeholders; common client wrapper distinguished from protocol; existing generic SDK stdio regression. |
| S12.06 | Seven-name README table compared to explicit registry; excluded application-only functions labelled, not advertised as MCP tools. |
| S12.07 | architecture.md Mermaid, module ownership, request flow, lifespan and collection/result invariants. |
| S12.08 | Current implementation matrix compares exactly three literal POST paths and closed bodies to source; published future filters/history distinguished. |
| S12.09 | security.md describes secrets, allowlist, trust boundaries, TLS, replay/byte/time/cleanup limits and residual risks. |
| S12.10 | local-dev.md has Windows PowerShell/Git Bash and macOS/Linux recipes, explicit interpreter/pip and unverified POSIX-platform caveat. |
| S12.11 | Current runbook boundary/troubleshooting and separately authorized future manual-validation procedure; no execution of Sprint13. |
| S12.12 | Allowlisted public Markdown/example review for private paths, personal identifiers, nonpublic hosts and credential assignments; no claim about ignored files, Git index/history or unknown source secrets. |
| S12.13 | attributions.md records five installed direct-license metadata values, source-reference audit and no vendored upstream source observed; project-license decision stays pending, no redistribution clearance. |
| S12.14 | README records G5 in the reviewed public-documentation scope, explicit release limitations and NOT_READY/G6 pending. |
| S14.01 | README/PRD/current inventory and seven registry names reconciled; no behavioral or registry change. |
| S14.02 | Method/route/body matrix and security guide compared to _QUERY_PATHS/_query; prices/stock page/limit only; mutually exclusive product filters. |
| S14.03 | Existing .env.example and generic MCP snippet reviewed: no real token/login/password, host example.invalid, absolute-path placeholders only. |
| S14.04 | AST imports show actual consumers of mcp/pydantic/httpx/anyio/python-dotenv; exact pins retained, no unused direct dependency to remove. |
| S14.05 | Explicit public root/tests/docs inventory and production imports: seven modules, no Docker/DB/migrations/UI/CI implementation; excluded trees not traversed. |
| S14.06 | Programmatic ordered tuple comparison requires only28 approved S12/S14 state changes; all task texts/order, Sprint13 and global checkboxes preserved; prior evidence read, not fabricated anew. |
| S14.07 | DEC-035 records consolidation versus operational/public release, direct pipeline and existing dependencies, history preservation and costs. |
| S14.08 | README/security/inventory retain refused filters/tools, no mutation/arbitrary HTTP/tenant, SKU exception, unknown currency/deposit/freshness and bounded visibility. |
| S14.09 | NOT_READY: bounded commercial evidence exists, but Sprint13/final global release criteria are not accepted; do not relabel as fully blocked commercial API. |
| S14.10 | README seven-tool table plus separately labelled application functions, actual inputs/defaults/output limits and evidence. |
| S14.11 | Public README/local-dev/configuration cover explicit interpreter, secure configuration ownership and generic stdio integration without client-brand dependency. |
| S14.12 | Optional maintainer handoff below, no executed Git/versioning/publication. |
| S14.13 | PRD1.12.0 dated31/10/2026, DEC-035 and affected current status reconciled; historical records remain dated. |
| S14.14 | Accept only reviewed documentation/offline behavior and historical bounded evidence as labelled; no new operational acceptance, V1 approval or waiver of Sprint13/global criteria. |

### Executed verification and boundaries

Baseline captured57 explicitly public files in managed scratch, including the
approved design/plan. Root-.venv `--version` returned Python3.14.3.
`.venv/Scripts/python.exe -B -m unittest discover -s tests -v` returned195
tests PASS in17.591s; `.venv/Scripts/python.exe -B -m pip check` returned
`No broken requirements found.` This is a new offline regression run, not
a recreation of historical ERP results or completion of Sprint13 tasks.
Direct distribution metadata matches all five pins; AST source inspection
confirms each dependency's actual consumer. License metadata is recorded in
attributions.md, not a project-license selection or legal certification.

The initial documentation audit correctly reported the pending new README
handoff anchor before this runbook section existed; it was supplied here,
not suppressed from link checking. A subsequent audit also caught12 existing
identifying lines in five historical documents. After the maintainer explicitly
approved the narrow exception, business/local-path references were replaced
with neutral placeholders in the two archives and Sprint5/9/11 plans. The
archive index now discloses redaction rather than claiming byte equality.
The first credential-empty check also mishandled CRLF in the unchanged
example; line-based inspection corrected the audit, not the example file.

After those edits, the offline suite again passed195 tests in9.144s and
pip check passed. Public audit:61 files,226 ordered PRD tasks,103 local
links/anchors, zero findings in the documented identifier/host/path checks.
Exact historical comparison allows only the12 approved substituted lines;
all other historical lines, task text/order/states and results remain.
Production, tests, manifest and neutral example are unchanged. Exactly seven
MCP names and three literal POST routes match the README/current matrix.
The final public comparison confirms exactly28 newly completed tasks,
S12.01–14/S14.01–14, among226 ordered tasks. Sprint13 remains0/20 open and
global/Definition-of-Done checkboxes are identical to baseline. Only the
approved documentation and historical identifying references differ.

### Independent review and final acceptance

The independent reviewer ran the complete offline suite:195 tests PASS in
8.959s, pip check PASS, Python3.14.3, and reran the public auditor. It
confirmed61 public files,103 local links/anchors, exact28 task transitions,
seven tools, three closed query contracts, five installed pins/licenses,
23 unchanged public production/test/manifest/example/ignore files and only
12 authorized historical line substitutions. No Critical/Important finding.

Two Minor reconciliation items were identified: the current archive paragraph
still described verbatim/immutable copies, and the execution plan steps were
not yet marked. Both are within the planned final documentation/status
reconciliation, not production fixes. A focused document check reproduced
both mismatches before correction; the current paragraph and plan were then
reconciled and are checked again with the final audit. No new runtime test
or retrospective operational evidence was invented. Existing long-line
style debt is unchanged; no new review finding is deferred.

The reviewer explicitly did not judge current credentials/TLS/ERP/permissions/
effects/coverage; clean installation or macOS/Linux; secrets in private files/
Git index/history/future publication sets; legal ownership/license or
transitive compliance/vulnerabilities; reproduction of old ERP observations;
visual Mermaid rendering or current external-link availability. These limits
are retained: code fences/structure and local links are checked, not rendered
diagrams or live provider contracts. No new release criterion or permission
is inferred. G5 passes only the reviewed public-documentation scope; the two
sprints are accepted in that scope, NOT_READY and G6 pending remain.

Final coordinator closure check: both focused document assertions passed
after failing before reconciliation; full195-test suite PASS/8.947s and
pip check PASS. The public scope/checklist/link/privacy auditor passed again
with the same61 files/103 links/226 task IDs and exactly28 approved state
changes. All18 execution-plan steps are now marked with their evidence.
No pending new review finding; no additional ERP/configuration/Git action.

Audit artifacts use explicit Hermes managed scratch netone-s12-s14. Initial
TMPDIR unexpectedly pointed to ordinary Local/Temp; only the newly created
public baseline was moved to managed scratch and TMPDIR was explicitly set
there before tests. No private configuration was involved. Public snapshots
and difflib replace Git; no index/history or secret-file checksum is claimed.

### Optional maintainer actions and remaining release blockers

1. Decide the project's license and confirm authorship/rights; retain required
   notices if distributing third-party artifacts. Installed direct metadata
   alone is not a transitive redistribution audit.
2. Privately review the exact proposed publication file set and Git index/
   history for secrets/commercial data. Ignore rules do not establish prior
   tracking safety. Do not blindly stage all files or publish historical
   secrets; incident response/rotation belongs to an authorized owner.
3. If desired, separately authorize Sprint13 scope: compatible clean-install
   proof without silently replacing the sole .venv, applicable acceptance
   matrix and a numeric real-call budget/configuration-read permission where
   needed. Preserve historical evidence, unknowns and the technical-SKU
   exception. Do not infer query permission from this handoff.
4. Only after reviewing actual acceptance and remaining blockers, decide on
   explicit commit/tag/push/release actions and destination. No such action,
   upload or permanent MCP connection has been performed here.

G5 is documentation-only within the reviewed public set. G6 and V1 remain
pending/NOT_READY. These sprints do not establish current credential validity,
live TLS/ERP behavior, remote multi-page/snapshot guarantees, unit/deposit
identity, freshness, all-tool real MCP coverage, clean installation or other
platforms. Existing long-line style debt remains. The Sprint13 checklist and
global/Definition-of-Done checkboxes are intentionally untouched.

## Sprint 13 — final validation ledger

PRD1.13.0 / DEC-036. The maintainer approved the design including VM11's
empty-result/HTTP404 distinction, then the plan and native execution.
Design: superpowers/specs/2026-10-31-sprint-13-design.md.
Plan: superpowers/plans/2026-10-31-sprint-13.md.
Offline execution uses managed scratch netone-s13, no Git helpers, and a
63-file public-only baseline. The preceding61-file baseline matched before
execution. No application/test/manifest change is planned.

### Historical pre-execution authorization checkpoint

Authorization ledger: offline/public-documents/synthetic probes APPROVED;
temporary clean installation APPROVED separately, including removal of that
temporary environment only; one private loader invocation APPROVED separately;
one real list_products POST/page1/limit1 APPROVED separately. The maintainer
answered all three independent consent questions explicitly. No remote attempt
or private read has occurred at this checkpoint. These later permissions, not
plan approval, admit only the exact temporary install and one-shot proof.

Evidence is collected below before any corresponding PRD checkbox is marked.
Synthetic success never establishes live credential/TLS/ERP acceptance.
S13.02/04/11 await execution evidence within those permissions;
recording a matrix and its blockers does not pass G6 or complete the sprint.

### Offline runtime and consumer evidence

Executed with the existing root .venv, Python3.14.3/win32. Direct metadata
matches mcp1.30.0, pydantic2.14.1, httpx0.28.1, anyio4.15.1 and python-dotenv1.2.4.
`python -B -m pip check` returned `No broken requirements found.` No install.
The Task1 tuple comparison passed: all sprint task IDs/text/order/states
unchanged and VM11 the sole revised VM criterion before evidence marking.

Actual root-interpreter commands/results:

| Command/scenario | Result | Scope |
|---|---|---|
| `-B -m unittest discover -s tests -v` |195 PASS/9.782s | Existing environment, synthetic only |
| `-B -m unittest discover -s tests -p 'test_mcp*.py' -v` |19 PASS/2.171s | Exact seven-tool discovery, actual SDK stdio and guarded synthetic consumers |
| `-B -m unittest discover -s tests -p 'test_server.py' -v` |5 PASS/1.808s | Protocol stdout, safe DEBUG stderr, malformed recovery and bounded EOF dialogue |
| `-B -m unittest discover -s <managed-scratch>/netone-s13 -p 'test_s13_probe.py' -v` |4 PASS/1.710s | Temporary offline harness; first run failed four expected missing-harness assertions |
| `-B <managed-scratch>/netone-s13/s13_offline.py imports config faults analysis` | All four modes PASS | Synthetic demonstrations below |

Commands use `.venv/Scripts/python.exe` explicitly; scratch paths are resolved
locally, not copied into public docs. TMPDIR was set to managed scratch before
tests. No real .env read, settings dump, ERP request, Git or install occurred.

Fresh imports exercised all seven modules with path-aware private-read guards,
HTTP-client construction/DNS/connect prohibited, stdout/stderr captured empty
and process environment unchanged. Guard self-check rejected nonexistent
synthetic .env paths before access while allowing the public manifest read.
Actual server.main/real loader with mocked file content and empty child
environment returned1 for missing origin and missing token, stdout empty,
fixed configuration_error diagnostics, and no client construction. Valid
synthetic loading preserved literal interpolation text, overrides and repr
secrecy without environment mutation. This is not private config acceptance.

Manual synthetic fault demonstrations called actual tools.list_products through
the existing client/guard/normalizer: valid empty terminal→not_found/error null;
403→error/authorization_error;404→error/not_found (endpoint);429→rate_limited;
ReadTimeout→timeout; invalid JSON→invalid_response. Each made one synthetic
attempt, with no replay. A separate two-page case preserved one useful record
and exact large Decimal/leading-zero ID after a second-page500: partial,
upstream_error, complete_dataset false. In total8 mock attempts,7 completed
response closes (timeout had no response) and7 completed transport/client closes.
No real permission/rate-limit/timeout was provoked or inferred.

Both actual application analyses ran without LLM/configuration using two mock
requests and two completed response/transport/client closes. Inventory retained
7 source records, excluded one conflicting reduced identity, analyzed5 and
reported low_stock2/unknown2 at threshold3, sample scope and metrics incomplete.
Catalog analyzed2 reduced identities/one product, preserving leading-zero
codes, exact large Decimal scale, false and null/absent/blank distinctions.
No unit/deposit sum, global KPI, real analytical evidence or MCP registration.

At this historical offline checkpoint, S13.01/03/05–10/12–17 had the evidence
above; S13.02/04/11 still awaited specific installation/private/live evidence
and S13.18–20 awaited audit/matrix/review. The later sections record those
results. This paragraph is not the current task status or renewed permission.

### Clean installation and closed one-shot operational budget

Separate consent authorized a new temporary clean environment in managed
scratch, installation/testing and removal of that environment only. The
destination did not exist before creation. Root `.venv/Scripts/python.exe -B
-m venv <managed-scratch>/netone-s13/clean-env` created Python3.14.3, followed
by its own `-m pip --isolated install --index-url https://pypi.org/simple
-r requirements.txt`, exit0. No detailed installation stdout log was retained;
subsequent distribution metadata confirmed the five exact manifest pins.
This is a newly created environment, not a reinstallation into root .venv.

Clean-interpreter `-B -m pip check` passed; guarded fresh imports of all seven
modules and real-loader/synthetic missing-config probes passed; its own
`-B -m unittest discover -s tests -v` passed195 tests/8.761s. Root direct
distribution versions still matched the pre-install snapshot. No upgrade,
global install or .env copy; Windows only, no lock/transitive/security claim.
Temporary-environment cleanup is recorded after its actual execution below.

Before remote execution the protocol harness passed11 tests/6.933s and the
project passed195 tests/8.754s. Harness regressions first failed before
implementation; checks detect rounded Decimal/null-to-zero corruption,
preserve metrics after HTTP500 and after receiving a row, reject consumed
markers/unapproved live launches and avoid treating an empty reply as observed
record fidelity. A separate synthetic regression found that a successful
child report could overwrite parent failure; it failed PASS versus FAIL_PROCESS,
then passed after preserving the parent outcome. No production change.

**Budget CONSUMED/CLOSED:** on2026-10-31T16:04:21.477379Z through
16:04:22.744658Z, the generic SDK stdio client initialized the actual server,
discovered exactly seven tools and called list_products once with
max_results=1/page_size=1/max_pages=1. One private load_config invocation in
the child used existing settings only in memory. Exactly one POST
`/app-web/api/v2/produto/reduzidos`, body page1/limit1, returned HTTP200:
one received/returned item, one page, partial=true, complete_dataset=false.
Independent field-by-field projection/Decimal/null/absence checks against the
same consumer response passed, as did structured/text JSON equivalence.
One response close, one transport close and one client close completed.

Original request guard/TLS/identity/size/time limits remained; an additional
hook restricted method/path/body and one attempt. No real transport replacement,
retry/redirect, login, rotation, .env write/move/checksum or additional discovery.
Only safe counts/codes/test times/booleans were retained; no source values,
origin/token/raw stderr/settings/response were written. The safe JSON report
was read back after execution. The exclusive live.started marker remains;
neither interruption nor evidence repair permits replay. No unused new budget.

S13.02/04/11 now have their specific evidence. The single real product sample
does not newly validate prices/stock, every tool, remote multi-page traversal,
global coverage/snapshot, deposit/freshness or undisclosed provider effects.
G3/G4 are not widened by the task count; global criteria/G6 remain unaccepted.

Authorized cleanup completed: only managed-scratch clean-env was removed after
its evidence was recorded; root direct versions still matched the before
snapshot. No additional environment remains from the clean-install probe.

### VM01–VM20 acceptance matrix

All commands use the explicit root interpreter unless marked clean-interpreter.
PASS applies only to the scope in the row, not every behavior of the ERP.
Observed by: native coordinator; date2026-10-31. Maintainer sign-off: pending.

| ID | Status | Evidence / command or scenario | Scope and remaining limit |
|---|---|---|---|
| VM01 | PASS | `.venv/Scripts/python.exe --version` → Python3.14.3 | Current Windows interpreter, not PATH or all platforms |
| VM02 | PASS | Clean and root imports, five pins match, pip check passes | Fresh clean Windows environment and existing root; no transitive lock/security audit |
| VM03 | PASS | Real load_config once in live child, configuration_loaded=true; synthetic override/no-mutation checks | Safe in-memory use for this one-shot; no settings display, no ongoing permission |
| VM04 | PASS | s13_offline config: actual main/loader, missing origin and missing token → exit1/fixed diagnostics/empty stdout | Mocked file and child environment; no live misconfiguration induced |
| VM05 | PASS | Actual SDK stdio initialize/list/call; server tests5 PASS | Synthetic protocol suite plus one real listing, no inbound service |
| VM06 | PASS | Exact seven-name discovery from SDK and registry/schema tests | No SKU/expanded/analysis tools added |
| VM07 | PASS | Registry and all guarded consumer tests; closed extra-forbid schemas | No writing/HTTP/configuration tools; advisory annotations alone not proof |
| VM08 | PASS | MCP invalid inputs/effective page_size tests → zero sends | Synthetic invalid types/extras/combined caps, no malformed ERP call |
| VM09 | PASS | One POST reduzidos/page1/limit1 via list_products, HTTP200/one item, fidelity/JSON/cleanup true | Real one-shot only; budget CLOSED; partial sample, not all-tool coverage |
| VM10 | PASS | unittest client/protocol401/403 cases, manual synthetic403 | Authentication/authorization distinct; no live permission change |
| VM11 | PASS | Manual synthetic valid empty→not_found/error null, HTTP404→error/not_found | Corrected criterion; endpoint error is not product absence |
| VM12 | PASS | Manual synthetic429/Retry-After and client tests → one attempt/no replay | No real rate-limit stress or automatic resend |
| VM13 | PASS | Manual ReadTimeout and second-page500 preserve error/useful partial data, completed cleanup | Synthetic failures, not observed ERP outage |
| VM14 | PASS | Manual invalid JSON→invalid_response; suite duplicate/compression/oversize cases | Synthetic streaming/parse limits, no raw payload diagnostics |
| VM15 | PASS | Multi-page/error/cut/duplicate tests and manual page2 failure | Offline pagination controls; real proof was one page, not remote traversal |
| VM16 | PASS | Catalog/product-field/stock/MCP tests and actual synthetic analysis demonstrations | Exact IDs/Decimal/null/absence/zero; live fidelity only same products response |
| VM17 | PASS | s13_offline analysis invokes both public consumers; counts/conflicts/scope asserted | Synthetic deterministic sample, application-only, no global KPI or unit sums |
| VM18 | PASS | Guarded fresh imports, SDK stdio with LLM/framework paths excluded | No LLM key needed; generic SDK, not every possible client |
| VM19 | PASS | Public .gitignore text has .env/.env.*/.venv and neutral-example exception | No Git/index/history inspection or prior-tracking guarantee |
| VM20 | PASS | s13_audit:63 public files/142 local links and anchors/zero bounded findings; DEBUG malformed/projection tests | Public set and safe diagnostics only; no universal secret detection/private-file audit |

### Public audit and release boundary

The temporary auditor passed with63 allowlisted public files,226 ordered PRD
tasks,142 local links/anchors,seven registry entries and three literal routes.
Only ten allowed current-document/design/plan files differ from the execution
baseline. Production, tests, manifest, examples/ignore and historical archives
remain identical. The tuple checker rejects unrelated state changes, any task
text/reordering and global-checkbox edits; its missing-implementation test first
failed and then passed. VM11 is the only revised VM criterion. The initial URL
candidate audit encountered intentionally malformed IPv6 negative-test strings;
the audit now classifies those without treating them as actual destinations.
This was a harness parsing limitation, not a production or credential finding.

G6/global acceptance is **BLOCKED**, not FAIL of the twenty scoped VM scenarios.
The mandatory section26/30 release checklists have not been individually accepted;
the preserved original .env has no historical baseline for a byte-equality
claim. This execution made no .env write/move, but does not invent historical
comparison evidence. Owner action: review/accept each remaining global criterion
against its scope, or explicitly decide a documented criterion amendment where
proof cannot be obtained; do not substitute administrative completion for proof.
Project license/publication decisions remain separately owned, not automatically
new VM09 prerequisites. No G6, V1, publication or extra ERP budget is granted.

S13.18 is supported by the bounded public/diagnostic audit and S13.19 by exactly
twenty classified VM rows. S13.20 records the review and outstanding blockers,
not a false declaration of final sprint/release acceptance.

### Independent review and final reconciliation

The independent read-only reviewer reran195 tests PASS/8.254s, twelve temporary
harness tests PASS/6.208s and pip check PASS. A nonwriting in-memory audit
confirmed63 files/142 links/226 task tuples,seven tools/three routes, no bounded
findings and only19 supported S13 state changes at that checkpoint; S13.20
was still open pending this reconciliation. Twenty Python files and the
manifest matched baseline. No Critical or Important finding.

One Minor identified earlier authorization/offline status paragraphs that could
be mistaken for current instructions when quoted alone. The scheduled final
status reconciliation labelled the pre-execution checkpoint and made its
historical offline status explicit. No production/harness change or sensitive
repeat was needed. Existing long-line debt is unchanged. Final coordinator
commands/results are recorded below after execution.

Historical protected-edit checkpoint: the final AGENTS.md approval initially
timed out, leaving stale final-review wording. The renewal question was also
unanswered; no retry or alternate path was used at that checkpoint. The
maintainer subsequently explicitly requested that the submission be sent again.
The normal protected patch then approved/applied only the final Sprint13 status
paragraph:20 evidenced tasks, completed review, CLOSED budget and G6 pending/
NOT_READY. The discrepancy and timeout are resolved, not current blockers.
This documentation-only follow-up grants no private read, query or Git action.

Review exclusions were assessed and retained, not silently discarded:

- Private/current credential validity and reproduction of the consumed real
  attempt: safe report only; no additional private read/ERP query authorized.
- Reproduction of removed clean installation and its unretained transaction
  stdout: accepted executed clean metadata/import/pip/test evidence only.
- Historical .env byte equality: unavailable baseline, no invented proof.
- All-tool live behavior, prices/stock, remote pagination/global coverage,
  snapshots/deposit/freshness and undisclosed provider effects: not established
  by one product sample or local guards; earlier bounded limits remain.
- Universal secrets/private files, Git/index/history/provenance/publication
  safety: bounded public audit only, no access to excluded material.
- Dependency advisories/transitive reproducibility/external lint/types,
  other operating systems/interpreters/every client: not executed or claimed.
- Licensing/legal clearance, maintainer sign-off/global/G6/V1: owner decisions
  and unaccepted criteria, not waived by task completion.
- Historical RED sequencing: recorded earlier executed evidence, not newly
  recreated by the reviewer; current twelve harness tests independently passed.

The coordinator retains public snapshots/diffs/ledger instead of Git helpers
or deleting evidence: Git remains forbidden and no commit history replaces the
record. Synthetic probe preparation proceeded independently while permissions
were pending; no sensitive action ran before the three explicit consents.
Costs of these choices: no Git/history audit, managed scratch can be pruned,
and safe operational proof cannot be reproduced without a new authorization.
This runbook therefore carries the durable findings and consumed budget.

Final coordinator verification after the review/reconciliation: root full suite
195 PASS/8.398s, temporary harness12 PASS/6.363s, pip check PASS and public
auditor PASS (63 files,142 local links/anchors,226 ordered tasks,seven tools,
three routes). Exactly twenty S13 states changed to complete; all task text/
order, sibling sprint states and global/DoD checkboxes are unchanged. The twenty
VM rows are complete and ordered. Only the ten allowed documentation/design/
plan files differ; production/tests/pins/archives/examples/ignore are unchanged.
No live probe/private read/install was repeated. At that checkpoint the final
AGENTS reconciliation awaited approval. Following the maintainer's later
explicit re-send request, the normal protected update succeeded and the plan
step is now complete; the earlier timeout is historical, not an active blocker.
This is20/20 task evidence with explicit blockers, not final sprint/G6/V1
acceptance or permission to publish. All execution findings/limits are above.
