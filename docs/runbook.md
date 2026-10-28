# Investigation runbook

This runbook records Sprint 0 investigation and Sprints 1–2 foundation evidence. Later authorized sprints must add commercial integration troubleshooting and the remaining VM01–VM20 execution evidence. No runtime scenario is marked PASS by inference from documentation. Historical sections retain their original scope; the current configuration status is recorded in the Sprint 2 section below.

## Scope and rules

- Date: 2026-10-27.
- Source of truth: PRD 1.1.0, section 28, Sprint 0. The maintainer authorized a documentation-only policy revision admitting three query POST candidates; not generic POST, runtime authorization or another sprint.
- Read-only inspection of local source and public upstream documentation only.
- No Git commands or `.git` edits. No ERP requests, token handling, environment installation, automated tests, fixtures or CI were performed.
- Local environment files were not opened or modified. An existence-only check confirmed `.env` is present; it was excluded from displayed file inventories. No content comparison or historical credential-revocation check was performed. Existing `.venv` was left unchanged.
- Public evidence excludes local legacy project identity, installation hosts, credentials and real commercial records.

## Executed inspection record

| Scenario | Exact command or manual action | Result | Sanitized evidence |
|---|---|---|---|
| Read project constraints | Read `PRD.md` and `AGENTS.md`; inspect `.env.example` and `.gitignore` through file tools | PASS | Planning-only project; no test/Git permission; empty credentials and `example.invalid` URLs. Historical GET-only policy was explicitly replaced in PRD 1.1.0 by narrow query POST candidate admission |
| Root inventory | `python -c "from pathlib import Path; print([(p.name, p.is_dir()) for p in Path.cwd().iterdir() if p.name not in ('.git', '.env')])"` (this expression was rerun inside the combined documentary audit) | PASS | Initial displayed root: PRD, agent instructions, example, ignore file and `.venv`; no application Python or requirements manifest. `.env` deliberately excluded; existence-only check confirmed its presence |
| Legacy integration | Text-only local search in `.py` files for `REDUCED_PRODUCTS_URL`, `STOCK_URL`, `netone-auth-token`, excluding environments/vendor directories; read matching `config.py` and `integrations/netone.py` with literal URLs redacted before display | PASS | Source locations and arguments in [API inventory](api-capabilities.md); two commercial POST calls, no source execution |
| SCSI source | Anonymous GitHub API tree/commit lookup and raw HTTP reads of the requested paths; independent coordinator reread of cited excerpts | PASS | Pinned revision and 34-file inventory in [reference audit](scsi-reference.md); tree not truncated |
| Official NetOne documentation | Browser navigation/read of O1–O19 listed in API inventory; wait for content hydration; no request submission | PASS | Product group: ten documented POST queries; separate POST login; no GET equivalent established |
| Generic URL extraction | Attempt `web_extract` on official quick start and reduced-product references | FAIL | Configured extraction backend was search-only; browser rendering provided an alternative, without changing configuration |
| Query semantic safety / S0.11 | Review documented methods and business-side-effect evidence under PRD 1.1.0 | BLOCKED | Three query POST candidates exist; no new evidence confirms absence of business mutation. Method/operation label alone is insufficient; S0.11 stays unchecked |
| Remote API validation | No call attempted | BLOCKED | Semantic-safety evidence, safe transport/configuration and explicit bounded-call authorization remain pending; no runtime authentication or data-fidelity claim. GET is no longer required |
| Agent-context reconciliation | After user authorization, applied targeted `AGENTS.md` patches reflecting docs and the PRD 1.1.0 policy | PASS | Tool-confirmed edits; current context records three narrowly admitted query POST candidates, business-mutation prohibition, S0.11/G0 blocked for validation, no runtime or later-sprint authorization |

## Sprint 0 acceptance ledger

The canonical task text remains in the PRD. This table maps each task to evidence rather than duplicating and paraphrasing the canonical checklist.

| Task | Result | Acceptance evidence |
|---|---|---|
| S0.01 | PASS | SCSI PRD read; architectural/convention excerpts and adaptation matrix in reference audit |
| S0.02 | PASS | Requested `core/`, `ai_agents/`, `docs/`, example and requirements retrieved/inventoried; key excerpts independently reread |
| S0.03 | PASS | Explicit rejected-pattern table, including Django, DB, Docker, UI and Celery |
| S0.04 | PASS | Legacy inspected as text only; no Git or source execution |
| S0.05 | PASS | L1 variable names and L2 header locations; no token value read |
| S0.06 | PASS | Product and stock call methods, arguments, timeouts, response handling and limitations recorded |
| S0.07 | PASS | Both `requests.post` call sites documented at L2 lines 28 and 68 |
| S0.08 | PASS | Anonymous official browser reads; extraction limitation and rendering workaround recorded |
| S0.09 | PASS | Endpoint table distinguishes legacy observations, published contracts and missing runtime validation |
| S0.10 | PASS | GET-equivalent investigation completed without speculative routes; negative result limited to inspected sources |
| S0.11 | BLOCKED | Revised criterion: confirm absence of business mutation for each candidate operation using its documented method; query POST admission is not proof; leave unchecked |
| S0.12 | PASS | Official reusable user token, ERP retrieval and POST login documented; OAuth/refresh/expiry unknown |
| S0.13 | PASS | Published paging, field/error contracts, documentation conflicts and unknown numerical limits inventoried; no invented quotas |
| S0.14 | PASS | `api-capabilities.md` contains sanitized source/method/path/evidence matrix |
| S0.15 | PASS | Decisions, unresolved questions, owner and requested proof recorded without identifying an installation |
| S0.16 | PASS | G0 explicitly BLOCKED for semantic-safety/runtime evidence; three policy candidates but zero operationally approved commercial tools/routes; product remains NOT_READY |

S0.10 is the preserved historical GET investigation, no longer a prerequisite for queries. S0.13 indicates an inventory of known contracts and unknown limits, not measured quotas. S0.11 and S0.16 wording was revised in PRD 1.1.0; their statuses did not change and no new checkbox was completed. S0.16 accepts a formal BLOCKED decision, not completion of semantic-safety assurance. Sprint 0 still has one blocked task and is not fully concluded.

## Operational handoff

The maintainer must review the exact documented POST query candidates for reduced products, prices and stock, establish no-business-mutation evidence through an explicit contract or technical provider confirmation, and resolve the relevant API-inventory conflicts. Safe configuration/transport and a separate bounded-call authorization are required before validation; tool release follows that evidence, not the documentation edit. Do not require a GET equivalent, request credentials in chat, regenerate a token, try the published test host, or treat query POST admission as arbitrary request permission.

Sprint 1 was subsequently authorized and partially inspected; see the Sprint 1 record below. G0 remains blocked. Do not call this checkout FOUNDATION_READY until actual foundation/runtime acceptance has evidence.

## Documentary verification

Historical approval event: the first protected `AGENTS.md` edit was not applied because its approval prompt timed out. No alternative write was attempted. The user subsequently requested renewed approval, and the targeted patch succeeded. This is no longer an active blocker.

Read-only audit commands were used to compare Sprint 0 IDs/order/status with this ledger, count the endpoint rows, check the upstream file inventory and inspect local Markdown links. These are one-off document inspections, not automated application tests or fixtures. A first combined audit command failed because the shell interpreted Markdown backticks embedded in a Python string; the command was corrected to use `chr(96)` and rerun. The corrected inventory reported 34 unique SCSI file paths and 11 endpoint rows (ten commercial POST queries plus login), no root application Python files, and `.env` present without reading it.

Historical final scenario for PRD 1.0.1, 2026-10-27: a one-off `python -c` read-only audit parsed the canonical Sprint 0 checklist and this table with regular expressions, compared their ordered IDs and checked/PASS mapping, inspected Markdown link targets, counted endpoint/source/file inventories, and matched the 19 official source URLs to the saved browser text. Result: PASS, exit code 0. Output: 16 Sprint 0 tasks, 15 checked, only S0.11 blocked, matching ledger, zero later-sprint checkmarks, 11 distinct endpoint rows, 19 official URLs with collected page text, 34 unique upstream file paths, zero broken local links, only public GitHub/Stoplight link hosts, and no root application module or dependency manifest. This verifies documentary consistency, not ERP behavior or full product acceptance. Author review also reconciled the API evidence, security boundaries and remaining unknowns; the SCSI audit provided a separate read-only upstream review, not a full independent final review of these deliverables.

## Authorized policy revision: PRD 1.1.0

Authorization: the maintainer explicitly approved revising the PRD after the proposal to admit documented query POSTs while forbidding commercial mutation. Scope chosen: only the three central product-query routes, with literal method/path plus a closed filter schema. Alternatives rejected: retaining GET-only as a requirement, or enabling POST generically. Policy admission is not a completed security review, evidence of ERP behavior, a real-call authorization or permission to begin Sprint 1.

Changes: planning requirements, diagrams, endpoint gates, security controls, risks, ADRs, decisions, acceptance criteria and affected future sprint wording; API inventory, reference note and agent context reconciled. POST query retries default to zero and commercial redirects are disabled; no body/method/route forwarding from MCP inputs. S0.11 and G0 remain blocked for missing semantic-safety/runtime evidence, rather than missing GET. All 16 Sprint 0 task IDs and their 15 checked/one unchecked statuses are preserved. No code, dependency manifest, remote call, Git operation or environment edit belongs to this revision.

Policy revision verification, 2026-10-27: one-off read-only `python -c` inspection compared all sprint task IDs/order/statuses against a pre-edit snapshot of the five public documents, reconciled the Sprint 0 evidence ledger, compared exact candidate method/path pairs across PRD/API inventory/agent context, checked version references, expected safety controls, obsolete GET-only clauses and local Markdown links. Result: PASS, exit code 0; 212 sprint task IDs/statuses preserved, Sprint 0 still 15 checked and only S0.11 pending, exactly three matching commercial query POST candidates, zero broken local links, no application module or dependency manifest created. This is documentary verification only, not a safety assertion about the ERP or an authenticated validation. The author reviewed remaining GET references as historical investigation, superseded policy, prohibitions on guessing methods or statements that HTTP method alone is insufficient; none establishes an active GET-only gate.

## Sprint 1 partial environment inspection

Date: 2026-10-27. The maintainer requested Sprint 1; this does not authorize ERP requests or change G0.

| Task | Scenario and evidence | Result |
|---|---|---|
| S1.01 / VM01 | `C:/Users/fstiz/AppData/Roaming/uv/python/cpython-3.14.3-windows-x86_64-none/python.exe --version` reported Python 3.14.3. `py -3.14 --version` did not select that runtime, although `py -0p` listed it. | PASS: a compatible interpreter is installed; the documented launcher command is not verified in this environment. |
| S1.02 | `.venv/Scripts/python.exe --version` reported Python 3.12.10; `pyvenv.cfg` confirms the same version. | PASS inspection; existing environment is incompatible with the required Python >=3.14. |
| S1.04 | Root names inspected with `pathlib`, excluding `.git`, `.env` and `.venv` contents; `.env` and `.venv` existence checked separately. | PASS: no root application modules or dependency manifest existed at inspection; user environment preserved. |
| S1.13 | Interpreter, launcher, environment compatibility and project state recorded here without credential values. | PASS; replacement of the existing `.venv` requires the maintainer's specific authorization. |

At that inspection, no environment was replaced, no dependencies were installed, and no ERP calls or Git operations were made. A Python 3.14 interpreter outside the existing `.venv` did not establish a clean installation.

### Follow-up after maintainer environment replacement

The maintainer subsequently recreated `.venv`. `.venv/Scripts/python.exe --version` reported Python 3.15.2; `.venv/Scripts/python.exe -m pip --version` reported pip 26.2.2 on Python 3.15. A dependency resolution attempt with `.venv/Scripts/python.exe -m pip install --dry-run mcp langchain langgraph pydantic httpx python-dotenv` failed while preparing `zstandard`: Microsoft Visual C++ 14.0 or greater was required. This was a dry run, not a successful dependency installation or proof that every version combination fails. Python 3.14.3 is separately available, but changing the maintainer's new `.venv` requires their decision.

S1.09: initial English README created, explicitly describing the unimplemented state. S1.10: `.gitignore` reviewed and extended to cover environment variants, Python bytecode, common local caches and logs while retaining `.env.example`. S1.03 and remaining tasks stay unchecked. No ERP call or Git command was made.

### Authorized replacement and foundation verification

The maintainer specifically authorized replacing `.venv`; `uv venv --clear --python <installed Python 3.14.3> .venv` replaced it in the same location. The uv-created environment initially had no pip; `.venv/Scripts/python.exe -m ensurepip` installed pip 25.3. Python 3.15 dependency-resolution failure above is historical, not an active blocker.

On Windows, Python 3.14.3 successfully installed MCP 1.30.0, LangChain 1.4.7, LangGraph 1.2.18, Pydantic 2.14.1, HTTPX 0.28.1 and python-dotenv 1.2.4. These are the direct planned stack requirements: only MCP is currently used by the foundation; the rest support later PRD-required layers. `pip install -r requirements.txt` subsequently reported requirements satisfied, and `pip check` reported no broken requirements. This was not a clean installation directly from the manifest: the exact versions were installed first by direct command. Transitive packages are not pinned; the direct pins do not constitute a lockfile.

VM01 PASS: `.venv/Scripts/python.exe --version` returned Python 3.14.3. VM02 and S1.12 PASS: one-off imports of the four application modules and the six direct dependencies succeeded. VM05/VM06/VM07: a local one-off subprocess sent MCP initialize and tools/list messages over stdio; process exit 0, JSON protocol responses for both requests, empty tool list, and diagnostics on stderr. This checks the empty foundation only; it does not validate commercial operations. `client.py`, `config.py` and `tools.py` are explicit documentation-only boundaries, not implemented functions or released tools.

S1.03 PASS: the existing environment was replaced only after explicit approval, at the same root path, without creating an additional environment. S1.05–S1.08 and S1.11–S1.12: manifest and minimal modules inspected; Python modules use English names and simple PEP 8 layout, and the only executable string literals use single quotes. No lint tool was run. No ERP call, Git command or `.env` edit was made.

Clean-install acceptance, 2026-10-27: the same `.venv` was cleared and recreated with the authorized Python 3.14.3, `ensurepip` bootstrapped pip, and `.venv/Scripts/python.exe -m pip install -q -r requirements.txt` completed with exit 0. `pip check` found no broken requirements; application and direct dependency imports passed. The MCP initialize/tools-list subprocess check was repeated after the clean install and returned only JSON protocol output, exit 0 and zero tools. This verifies the Windows environment and current manifest, not other operating systems, commercial API access or V1 completeness.

## Sprint 2 — central configuration

Date: 2026-10-27 (local session). Authorization: the maintainer requested Sprint 2 and approved the recommended legacy-origin compatibility design. Scope: offline configuration and sanitized startup, not login, HTTP transport, commercial tools, Sprint 3 or remote validation. PRD implementation revision: 1.1.1. See [configuration](configuration.md) and [the execution plan](superpowers/plans/2026-10-27-sprint-2.md).

All Python scenarios below were one-off `.venv/Scripts/python.exe -c` commands executed interactively. No application test files, automated suite, pytest, fixtures, CI, second environment or new dependency was created. Synthetic values identify their origin and were not presented as ERP responses. In-memory substitutions in the loader scenario were restored in `finally` and did not modify the real file.

| Task / VM | Exact command or manual scenario | Result | Sanitized evidence |
|---|---|---|---|
| S2.01 / VM20 | Read `.env` bytes locally; regex extraction prints assignment names only; no value output | PASS | Existing names: TOKEN_NETONE, REDUCED_PRODUCTS_URL, STOCK_URL, LOGIN_NETONE, SENHA_NETONE |
| S2.02 | Compare absolute location and SHA-256 of `.env` against the pre-code scratch baseline, without displaying hash or contents | PASS | Same path and exact bytes; file never written, moved or replaced |
| S2.03 / VM03 | Call `load_config()` with root file reads replaced in memory with synthetic assignments; separately remove the file via a synthetic FileNotFoundError and supply process settings | PASS | Explicit file loading and process-only loading work; no environment writes by loader |
| S2.03 / VM02 | Fresh subprocess imports config/server/client/tools while `.env` read attempts raise, with captured stdout/stderr and environment comparison | PASS | Imports succeed without reading `.env`; no stderr; environment unchanged |
| S2.04 / VM04 | `_validate()` with valid base and mixed-case/default-port legacy URLs; reject userinfo, wrong scheme, malformed host/port, query, fragment, encoding, controls, unexpected path and inconsistent origins | PASS | Legacy origin derivation works; invalid values produce fixed errors without URL or token |
| S2.05 / VM06–VM07 | Inspect load_config signature and server/tools code; MCP tools/list over stdio with synthetic process configuration | PASS | Public loader accepts no arguments; tools.py remains empty boundary; zero registered tools, no MCP configuration/HTTP/tenant surface |
| S2.06 / VM03–VM04 | Supply synthetic valid, missing, blank, non-ASCII and CRLF tokens | PASS | Structural token validation only; no login or permission/expiry claim |
| S2.07–S2.08 / VM04 | Check defaults and each numeric lower/upper bound; reject below/above, blank, NaN, infinity, fraction, whitespace, exponent, non-ASCII digit and excessive-length strings; reject DEBUG | PASS | Defaults 15 seconds / 100 results / 5 pages / 0 retries / WARNING; ranges match configuration reference |
| S2.04/S2.06/S2.08/S2.11 | Combined synthetic validation command: 70 invalid cases, valid legacy derivation, numeric boundary acceptance, frozen settings, safe repr and environment comparison | PASS | 70/70 rejected safely; URL/token absent from repr/errors; settings immutable; environment unchanged. First command emitted a Python SyntaxWarning from a backslash in its synthetic probe literal, not from application source |
| S2.03/S2.08/S2.11 | Eight loader scenarios: synthetic file, process override, empty process override, malformed syntax, duplicate key, missing file, unreadable file and literal dollar interpolation | PASS | All eight observed results true; read hook and environment restored; no expansion of `${DO_NOT_EXPAND}` |
| S2.09 | Inspect `.env.example` | PASS | Empty credential values, example.invalid origins, literal candidate paths and documented defaults; copying over `.env` is prohibited |
| S2.10 | Read README and configuration reference, compare names/defaults/ranges with implementation | PASS | Migration through process configuration preserves existing file; login/password names ignored; DNS/TLS and transport limitations explicit |
| S2.11 / VM05–VM07 / VM18 | Subprocess `[sys.executable, absolute_server_path]` with synthetic settings, from parent directory; send initialize, notifications/initialized and tools/list JSON-RPC lines; capture outputs | PASS | Exit 0, two protocol replies, zero tools; no synthetic token or origin in output. No LLM key needed by application code; no LLM called |
| S2.11 / VM04 | Same subprocess with empty process TOKEN_NETONE | PASS | Exit 1; stdout empty; stderr exactly one configuration_error line; no raw exception or values |
| VM02 | `.venv/Scripts/python.exe -m pip check` | PASS | No broken requirements found; no installation or manifest change |
| Current operator configuration / VM03 | Call `load_config()` without overrides; print only ConfigurationError. Follow-up inspects rejection categories, never URL values | BLOCKED | REDUCED_PRODUCTS_URL has a literal-route mismatch; HTTPS was not reported as the problem. No correction, guessed route or ERP request attempted |

One initial import-inspection probe replaced every `Path.read_text` call, including dependency resource reads, and failed. It was corrected to reject only `.env` reads; the fresh corrected subprocess passed. This probe failure is not an application import defect. Source line-length inspection identified overlong lines, which were shortened; final inspection reported none above 79 characters. No configured formatter/linter was installed or claimed. A later oversized combined command failed at the shell quoting boundary before Python execution; it was split into three shorter commands, all of which completed successfully.

The installed root interpreter remains Python 3.14.3. Configuration safety validation is offline and structural. Current installation readiness remains BLOCKED on the operator's URL decision; leave `.env` unchanged and supply corrected operator-approved process configuration if needed, overriding conflicting legacy URL references together. Do not infer a replacement URL from the error or request the value in chat.

G0 and S0.11 remain BLOCKED; G1 is not complete because Sprint 3 transport/authentication evidence is absent. A zero-tool MCP handshake and a masked token do not validate remote access, DNS rebinding controls, TLS, permissions, token freshness, or no-business-mutation behavior. There were no ERP requests, authentication calls, Git commands, commercial tools, environment replacement or writes to the real `.env` in this sprint.

### Independent review and final configuration gate

Date: 2026-10-28 (the local session crossed midnight). A fresh read-only reviewer inspected the implementation, relevant PRD/design and configuration docs. No Git, `.env` read, remote request or file edit was used by the reviewer. One concrete medium-severity defect was reported: urllib accepts a bracketed IPvFuture hostname, which fell through `ip_address()` failure into DNS validation and lost its brackets. The coordinator independently reproduced acceptance of both the invalid base and the mixed base/legacy authority before fixing the DNS fallback to reject bracketed non-IP hosts. Supported IPv6 remains accepted. No other concrete defect or deferred minor was reported; the fix was validated by execution, not a second review.

Final commands: three shorter `.venv/Scripts/python.exe -B -c` scenarios repeated validation, loader and MCP checks after the fix. Results: PASS, exit 0 for each command; 73 invalid synthetic configurations rejected without leaking values (the original 70 plus three IPvFuture cases), accepted defaults and numeric boundaries, legacy normalization, IPv6, frozen settings and safe repr; eight loader scenarios passed with state restored; MCP without LLM API-key variables returned two protocol replies and zero tools, exit 0, from a different working directory; invalid token returned exit 1 with empty stdout and exactly the sanitized stderr message. SHA-256/location comparison confirmed original `.env` preservation without publishing a hash. Final Python line-length inspection reported no lines above 79 characters.

S2.12 result: configuration security gate PASS (offline implementation acceptance). The current operator installation remains BLOCKED by the existing literal-route mismatch. G0, S0.11, full G1, commercial access and V1 acceptance did not change. The Sprint 2 PRD checklist is complete only for its twelve configuration tasks; no later sprint is authorized or completed.

Final documentary audit, 2026-10-28: one-off `.venv/Scripts/python.exe -B -c` compared all sprint task IDs/order/statuses against the pre-code scratch baseline, checked local Markdown link destinations, `.env` location/hash and empty example credentials. PASS, exit 0: 212 task IDs/order preserved, exactly S2.01–S2.12 changed to checked, Sprint 2 12/12, no other sprint status changed, zero broken local links, original `.env` unchanged and all three example credential values empty. A fresh `.venv/Scripts/python.exe -m pip check` again reported no broken requirements. This is offline documentary/dependency verification, not API acceptance.
