# Resumable inventory Implementation Plan

> For agentic workers: use superpowers:executing-plans inline, with a fresh independent reviewer before real execution. This is the execution breakdown of the already approved proposal, not a new approval gate.

**Goal:** Paginate the visible catalog and inventory through bounded MCP blocks and return observed oil products with positive known stock.

**Architecture:** Stateless `start_page` extension to the existing collector and list_products; add list_inventory. A temporary external MCP consumer reconciles endpoint blocks in memory. No persistent catalog or server-side join.

**Tech Stack:** Existing Python >=3.14,<4 and five unchanged direct pins, unittest, MCP stdio, HTTPX guarded transport.

**Spec:** `.hermes/plans/2026-10-31_163933-consulta-completa-produtos-com-estoque.md`, approach A explicitly approved in conversation.

## Global constraints

No Git commands/helpers/worktrees, commits, installs, commercial writes, login, redirects/retries, .env mutation or unrelated profile changes. Preserve historical sprint/global checkboxes. Source edits in existing checkout are authorized by the approved plan; use public-file scratch snapshots instead of Git worktree helpers. Private reads only via server loader. Campaign budget <=1200 HTTP attempts, page size <=50, products/stock only, 45 minutes including remote validation. Keep 1 MiB responses and existing timeout/cleanup guards. Return commercial values only to operator, retain safe structural evidence only.

## Interfaces and review focus

Collector: `_collect(operation, *, start_page=1, existing keyword arguments)`; strict integer 1..1000000, enforce last requested page in same range before sending. Defaults unchanged.

Add QueryResult fields `start_page`, `first_page`, `last_page`, `next_page`, `block_complete`, `endpoint_exhausted`. first/last refer to fully validated/normalized accepted pages, not attempted pages. next_page is available only after a safe block with published pagination, no error/no-progress/duplicate/conflict. block_complete means valid local work ended normally at a configured block budget or endpoint; partial global scope can still have block_complete=true. endpoint_exhausted means terminal endpoint metadata accepted, not global coverage. complete_dataset additionally requires start_page=1 and existing anomaly checks.

Review focus: suffix totals are not whole-traversal totals; corrupt pages never advance safe progress; continuation bounds must not overflow HTTP limit; identities/totals must reconcile across separate calls; quantity and category ambiguity must not become false commercial positives.

## Task 1 — bounded transport continuation

Files: client.py, catalog.py; tests/test_pagination.py (new, synthetic).

- [ ] Write failing tests for start_page=2 terminal suffix, bounded next_page, page/row caps, default page 1, invalid types/bounds/no HTTP, invalid metadata and preserved progress after later errors, empty/repeated/conflicting pages, concurrent independent start pages.
- [ ] Run `.venv/Scripts/python.exe -B -m unittest discover -s tests -p test_pagination.py -v` and observe missing continuation failures.
- [ ] Implement the interface above; retain closed query body and all guards. Whole totalElements reconciliation stays strict for start=1; for suffix blocks enforce rows <= totalElements but do not pretend block rows are the whole total.
- [ ] Run focused tests and full suite; record real output in execution ledger.

## Task 2 — application and MCP listings

Files: tools.py, mcp_tools.py, tests/test_pagination.py, tests/test_mcp_tools.py, tests/test_mcp_stdio.py, tests/mcp_stdio_fixture.py, tests/test_server.py if its explicit registry asserts seven.

Interfaces: list_products(..., start_page=1); list_inventory(client, max_results=20, *, page_size=None, max_pages=1, start_page=1) -> dict. Listing models share strict start_page. Inventory output carries the same unknown-deposit/freshness caveats as check_inventory.

- [ ] Test missing list_inventory and rejection/continuation behavior first; watch failures.
- [ ] Implement shared listing-input validation, additive stock tool and output caveats. Preserve old seven-tool argument defaults.
- [ ] Update exact expected registry to eight and exercise both listings at page>1 via generic stdio. Invalid start_page/extra args/effective limits must cause invalid_arguments and no HTTP.
- [ ] Run focused and complete suites plus pip check.

## Task 3 — external consumer and reconciliation

Files: managed scratch only; Python consumer and synthetic tests. No permanent inventory module or runtime cache in the project.

- [ ] Test a two-page synthetic MCP campaign, changing totals, repeated pages/identities, source conflicts, budget interruption, exact reduced IDs/zeros, Decimal signs/null/absence, oil accents/plural and accessory ambiguity.
- [ ] Implement ClientSession/stdio consumer using list_products/list_inventory one request per block, size 50 fixed. Track request/time caps outside tool-local budgets and guard actual HTTP attempts in a temporary server launcher without weakening production guard.
- [ ] Keep all business records in memory; only safe counts/codes/cleanup evidence on disk. Emit selected product values only into an operator-facing terminal result.
- [ ] Verify traversal from page 1, contiguous progress, consistent metadata/counts and unique unambiguous identities before declaring coverage. No provider snapshot claim.

## Task 4 — documentation, independent review, integration

Files: PRD.md, README.md, AGENTS.md and docs/{api-capabilities,security,configuration,runbook}.md; current overlays supersede historical checkpoints only for this approved slice.

- [ ] Record DEC-037/PRD1.14.0 for eight tools/continuation, unchanged global gates and budgets. Keep all old sprint checkbox states unchanged.
- [ ] Dispatch read-only independent reviewer over public baseline diffs, plan and synthetic results; no private access or ERP sends for reviewer.
- [ ] Resolve Important/Critical findings with RED->GREEN tests and full green suite.
- [ ] Update only mcp_servers.netone through supported Hermes CLI to eight-tool include, max_results50/max_pages1, sampling disabled. Read back exact target; verify hermes mcp test netone.

## Task 5 — authorized real campaign and close

- [ ] Run approved bounded campaign once, using same-process private loader and guarded MCP stdio. Page 2 success on each endpoint is part of the campaign, not extra duplicate validation.
- [ ] Stop on error, inconsistent progress, budget/time bound, or full traversal. Do not silently retry or enlarge quota.
- [ ] Return actual code/description/positive quantity list, category ambiguities and unknown/conflicting stock counts. Compute totals programmatically. If incomplete say so explicitly.
- [ ] Update safe runbook consumption and execution ledger; no business values in repository. Run final offline suite and verify unchanged unrelated checkboxes/pins using public snapshot. No release/commit/publication.

## Execution ledger

Ruling: use this approved checkout directly and managed scratch baseline/ledger instead of Git-based workflow helpers, because Git commands are prohibited by the approved scope.
Ruling: implementation is inline with one independent final review; this minimizes shared-interface coordination and preserves the review explicitly promised in the approved proposal.
Pre-flight: collector metadata -> listings -> MCP -> consumer share the exact pagination fields above. Consumer requires block_complete and endpoint_exhausted rather than overloading complete_dataset on suffixes.
