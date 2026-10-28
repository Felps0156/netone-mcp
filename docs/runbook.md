# Investigation runbook

This is the Sprint 0 evidence log, not a completed installation or runtime runbook. No application modules or dependency manifest exist yet. Later authorized sprints must add setup, stdio/tool discovery, troubleshooting and VM01–VM20 execution evidence. No runtime scenario is marked PASS by inference from documentation.

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

Sprint 1 was not started. If separately authorized, offline foundation work can proceed while G0 remains blocked, but `.venv` compatibility/replacement needs the maintainer's decision. Do not call this checkout FOUNDATION_READY until actual foundation/runtime acceptance has evidence.

## Documentary verification

Historical approval event: the first protected `AGENTS.md` edit was not applied because its approval prompt timed out. No alternative write was attempted. The user subsequently requested renewed approval, and the targeted patch succeeded. This is no longer an active blocker.

Read-only audit commands were used to compare Sprint 0 IDs/order/status with this ledger, count the endpoint rows, check the upstream file inventory and inspect local Markdown links. These are one-off document inspections, not automated application tests or fixtures. A first combined audit command failed because the shell interpreted Markdown backticks embedded in a Python string; the command was corrected to use `chr(96)` and rerun. The corrected inventory reported 34 unique SCSI file paths and 11 endpoint rows (ten commercial POST queries plus login), no root application Python files, and `.env` present without reading it.

Historical final scenario for PRD 1.0.1, 2026-10-27: a one-off `python -c` read-only audit parsed the canonical Sprint 0 checklist and this table with regular expressions, compared their ordered IDs and checked/PASS mapping, inspected Markdown link targets, counted endpoint/source/file inventories, and matched the 19 official source URLs to the saved browser text. Result: PASS, exit code 0. Output: 16 Sprint 0 tasks, 15 checked, only S0.11 blocked, matching ledger, zero later-sprint checkmarks, 11 distinct endpoint rows, 19 official URLs with collected page text, 34 unique upstream file paths, zero broken local links, only public GitHub/Stoplight link hosts, and no root application module or dependency manifest. This verifies documentary consistency, not ERP behavior or full product acceptance. Author review also reconciled the API evidence, security boundaries and remaining unknowns; the SCSI audit provided a separate read-only upstream review, not a full independent final review of these deliverables.

## Authorized policy revision: PRD 1.1.0

Authorization: the maintainer explicitly approved revising the PRD after the proposal to admit documented query POSTs while forbidding commercial mutation. Scope chosen: only the three central product-query routes, with literal method/path plus a closed filter schema. Alternatives rejected: retaining GET-only as a requirement, or enabling POST generically. Policy admission is not a completed security review, evidence of ERP behavior, a real-call authorization or permission to begin Sprint 1.

Changes: planning requirements, diagrams, endpoint gates, security controls, risks, ADRs, decisions, acceptance criteria and affected future sprint wording; API inventory, reference note and agent context reconciled. POST query retries default to zero and commercial redirects are disabled; no body/method/route forwarding from MCP inputs. S0.11 and G0 remain blocked for missing semantic-safety/runtime evidence, rather than missing GET. All 16 Sprint 0 task IDs and their 15 checked/one unchecked statuses are preserved. No code, dependency manifest, remote call, Git operation or environment edit belongs to this revision.

Policy revision verification, 2026-10-27: one-off read-only `python -c` inspection compared all sprint task IDs/order/statuses against a pre-edit snapshot of the five public documents, reconciled the Sprint 0 evidence ledger, compared exact candidate method/path pairs across PRD/API inventory/agent context, checked version references, expected safety controls, obsolete GET-only clauses and local Markdown links. Result: PASS, exit code 0; 212 sprint task IDs/statuses preserved, Sprint 0 still 15 checked and only S0.11 pending, exactly three matching commercial query POST candidates, zero broken local links, no application module or dependency manifest created. This is documentary verification only, not a safety assertion about the ERP or an authenticated validation. The author reviewed remaining GET references as historical investigation, superseded policy, prohibitions on guessing methods or statements that HTTP method alone is insufficient; none establishes an active GET-only gate.
