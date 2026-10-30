# NetOne API capability evidence

Initial investigation: 2026-10-27. Sprint 9.5 offline contracts below supersede
the earlier search defaults only; DEC-027/030/031 evidence remains bounded.
PRD1.9.3 / DEC-032 records Sprint9.5 complete offline,170 tests PASS after
independent review and a normalization-empty Unicode fix; pip check PASS.
Sprints 5–8 are accepted within their bounded evidence; technical codigoSku
remains unvalidated. Sprint 9 exposes seven previously observed application
capabilities via MCP with offline integration and a separately authorized
real MCP listing. S9.12 complete, G3 PASS in this bounded scope and Sprint9
complete; V1 NOT_READY. No new ERP/configuration read is
authorized; all observation budgets remain closed. The section below
supersedes earlier empty-registry/no-Sprint9 instructions only. Remaining
sections are historical evidence checkpoints, not renewed budgets. See
[the field inventory](product-field-priority.md) for its distinct samples.

## Sprint 9.5 — local optimization contract

The maintainer approved the [design](superpowers/specs/2026-10-29-sprint-9-5-design.md)
and [plan](superpowers/plans/2026-10-29-sprint-9-5.md). This changes local
search and serialization, not the HTTP allowlist or operational permissions.
Earlier sections below retain their historical defaults/checkpoint evidence.

### Inspected universe versus returned matches

`search_products(client, query, max_results=100, *, max_items=20)` remains
literal casefold substring matching in description/product_mask/sku, without
accent folding. max_results still counts received source rows, including
nonmatches and duplicates; an explicit legacy value20 still caps inspection
at20. Only the omitted default changes to100. max_items independently caps
returned matches; both accept strict integers1–1000. The configured row cap
and page cap always prevail. Page size remains min(50,effective row budget),
fixed throughout; insufficient residual budget stops rather than shrinking
offsets. Deadline remains four configured phase-timeout seconds, with the
existing bounded shielded cleanup allowance. No early stop at the first match.

QueryResult adds inspection_limit, page_limit, page_size and deadline_seconds
(null for manually constructed results without known budgets). All existing
metadata and fields remain. Search adds requested_max_results,
requested_max_items, output_limit=min(max_items,inspection_limit), matched_count
before output cut, output_truncated and collection_complete. Actual executed
work remains rows_received/pages_fetched/returned_count. A cut sets partial,
complete_dataset=false and output_limit_reached, while collection_complete
retains pre-cut collection completeness. Existing errors/warnings survive,
including a later error when every source item is filtered out. A valid
complete visible traversal alone supports not_found; no ERP-wide absence or
stable snapshot follows from it. retrieved_at is not stock freshness.

Synthetic examples: default with row cap100/page cap5 may read two50-row
pages and return up to20 matches. max_results20 keeps a20-row ceiling.
max_results100/max_items1 still inspects its bounded universe but returns
one match; a config cap10 prevails over the requested100. Zero matches never
enlarge a budget or trigger retries.

Only search_products changes its MCP defaults and adds max_items. Its strict,
extra-forbid schema exposes no lexical mode, suggestions or configuration.
The other six tools retain max_results20 and their existing inputs; listing
still defaults to one page. Technical SKU/expanded search are not registered.

### Expanded lexical search — application only

`search_products_expanded(client, query, *, required_terms=(),
suggested_terms=(), max_results=100, max_items=20)` uses the same bounded
single traversal. The explicit new output default20 replaces the former
absence of a separate output ceiling. Terms/patterns are prepared once and
each description is normalized once for comparison. Source values and exact
identity lookups are unchanged.

Only an unambiguous leading reviewed product type (manopla or punho) is
separated from the remaining phrase. The suffix becomes an additional
mandatory textual restriction alongside required_terms. For example,
`manopla LS2` can find `Punho LS2`, but not LS20 or LS2 only in a mask.
Unknown/ambiguous multiword phrases stay literal and do not use alternatives,
including suggestions, with ambiguous_query_literal_only. Callers can instead
supply a simple product type and explicit required_terms. No brand/model
fields, compatibility, semantic parser or commercial equivalence are inferred.

Expanded comparisons use NFKD/casefold without combining marks and Unicode
word boundaries; internal punctuation is literal and regex-escaped.
Queries, restrictions and suggestions that become blank after this
normalization are rejected before collection, including derived restrictions. Hyphens
can delimit a word; punho does not match empunho, LS2 does not match LS20,
and plural variants are not inferred. The reviewed list remains only
manopla/punho; suggestions stay suggested and are never persisted. Duplicate
normalized terms preserve direct/reviewed/suggested precedence. Direct items
sort first, then reviewed, then suggested, stably within each class. Output
cuts preserve items/matches alignment; unmatched restrictions are counted as
unverified, not established incompatibilities. Duplicates/conflicts remain
conservative and the coverage/snapshot disclaimer remains explicit.

### O5/O4 reinspection and future directed-query plan (no filter implemented)

Anonymous rendered official documentation was reread on2026-10-29 after
hydration; no Send action, configuration read or ERP call. The generic URL
extractor was search-only, so the browser supplied the operation bodies.

| Endpoint/source | Published request and response | Existing operational evidence | Decision/remaining gap |
|---|---|---|---|
| [O5 prices](https://net1ti.stoplight.io/docs/erp-api-v2/79683209728d7-busca-precos) | idsProdutos:array[number], idsReduzidos:array[number], mascara:string, ultimaAlteracaoTimestamp:string; page:number/default1, limit:number. Response idProduto/idReduzido:number, retail/wholesale amounts and table descriptions; pagination fields in schema but absent from displayed example. | S8.14 page1/limit1 only, local exact product_id selection. No real price-ID filter evidence. | Names/array shape are clear; combinations, batch/numeric ceilings, exact filter enforcement and termination guarantees are not specified. Plan one identity filter only; no implementation/admission/validation approval in this sprint. |
| [O4 stock](https://net1ti.stoplight.io/docs/erp-api-v2/47f2f0f5255d2-busca-estoque) | idsReduzidos:number in schema, array in example; idDeposito:number, codigoSku:string, comAlteracaoDesdeTimestamp:string, page:number/default1 and limit:number. Response idReduzido:number; quantity is physical minus reservations. Pagination fields in schema, absent from example. | S8.14 page1/limit1 only, local exact reduced_id selection. | Filter remains BLOCKED: supplier must resolve number versus array and confirm identity/pagination behavior. No format chosen from legacy/O3/O5. Deposit omission selects user's configured deposit; identity/freshness remain unknown. |

Future implementation requires separate endpoint admission, implementation
and bounded real-validation permission. O5's minimal candidate body is
page/limit/idsProdutos=[validated integer] for product identity, without
idsReduzidos/mascara/timestamp combinations. O4's candidate body shape cannot
be finalized until its conflict is resolved. No deposit/branch selection or
new route is proposed. All future filters must be internally constructed,
validated before send, fixed across pages and isolated concurrently, with
atomic rejection of a page containing another normalized identity.

The current textual product_id/reduced_id contracts remain lossless. A
future numeric adapter must reject incompatible identifiers without sending:
leading zeros, whitespace, signs, non-ASCII digits and noncanonical text must
not be stripped/coerced into another identity. A canonical nonnegative
integer subset with a defensive local bound may be proposed separately;
number in published docs alone does not supply that bound. Unsupported
identities require the caller to explicitly choose the existing bounded
local lookup, never automatic fallback after a filtered-query failure.

Planned regressions in test_client.py/test_sprint8.py: exact product versus
reduced identity; invalid textual IDs/bool/out-of-range rejected pre-send;
other identity rejects the whole page; terminal empty versus HTTP404/error;
fixed filtered pagination; concurrent IDs/budgets; all matching reduced
variants and source price tables preserved, not first-match/table selection.
For a target absent from a prefix, local fallback still spends its bounded
rows and remains partial. A directed filter could reduce candidate rows,
but requests/pages depend on matching variants and provider behavior; there
is no guaranteed one-request result or measured ERP speedup. O4 resolution
is owned by the maintainer/provider; required proof is a coherent official
contract or explicit supplier clarification, then separately approved checks.

### Serialization and synthetic cost

QueryResult no longer recursively copies records before serializing them;
CatalogRecord projects immutable fields shallowly, converts Decimal to exact
strings and returns fresh JSON containers. All prior values and populated-
first presentation survive. MCP textual JSON is compact, ensure_ascii=true,
allow_nan=false, with both structuredContent and equivalent text retained.
No null/key/warning or commercial projection was removed.

One fixed50-record synthetic payload with two Decimal amounts per record
required200 amount deepcopy calls before and0 after. Comparing the same
current payload, spaced JSON was27017 bytes and compact JSON24783 bytes:
2234 bytes/8.27% less in the textual representation, not the whole MCP wire
envelope. Search metadata/expanded provenance add their own bytes. Coverage
fixture: explicit20 read1 page/20 rows/0 matches; default literal and expanded
each read2 pages/51 rows/1 match with identical page/limit bodies. Expanded
terms did not multiply HTTP work. This is more coverage, not fewer requests
than the old20-row universe. Commercial fixtures retained3 price records and
2 stock records from3 rows/one request each, including identity conflicts as
partial rather than discarding variants. All figures are synthetic, not ERP
measurements; final regression/review results are recorded in the runbook.

## Sprint 9 — approved MCP exposure (DEC-030; historical defaults)

| MCP tool | Guarded POST route suffix | Closed body | Existing real application evidence |
|---|---|---|---|
| search_products | produto/reduzidos | page/limit | S6.13 |
| search_product_by_code | produto/reduzidos | page/limit/mascara | DEC-025 |
| get_product_details | produto/reduzidos | page/limit/idsProdutos singleton | S7.11 ID |
| search_product_by_ean | produto/reduzidos | page/limit | S7.11 EAN |
| get_product_price | produto/precos | page/limit | S8.14 |
| check_inventory | produto/estoque | page/limit | S8.14 |
| list_products | produto/reduzidos | page/limit | S8.14 |

Every suffix above is prefixed literally by /app-web/api/v2/; no new
route, filter or method is admitted. Query intent under DEC-017 is accepted
with residual unknown internal effects, not proof by POST or HTTP200.
The existing token/TLS/byte/time/pagination/cleanup protections remain.

MCP schemas are strict and extra-forbid; all expose max_results1–1000/
default20, counting inspected rows and capped by configuration. Query is
text1–200; commercial code/EAN/price product identity/stock reduced identity
are text1–256. Details product_id is integer0–9223372036854775807. Listing
starts at1, defaults max_pages1, accepts bounded explicit max_pages1–100
and page_size1–1000/null constrained by the effective row budget. No
arbitrary configuration/HTTP arguments or currency from the model.
MCP price currency stays unknown/null; the application retains its trusted
operator-confirmation option. Business code and technical SKU stay distinct.

NetOneMCP specializes public FastMCP list_tools/call_tool methods to avoid
implicit SDK preprocessing/coercion and exception/input echo. Structured
payload and equivalent JSON text preserve application partial/error/empty
states, exact Decimal strings and nulls. status error sets isError=true;
partial keeps records/error metadata with isError=false. Input/unknown/
unexpected errors have fixed messages. Protocol cancellation propagates.

Technical SKU and expanded search are not registered: their existing offline
coverage does not supply their missing real-function observation. This is
an explicit restriction, not an inference from shared endpoint support.
All auxiliary routes and analysis/write tools remain unavailable.

Offline149 tests passed in7.567s before review; generic ClientSession over
stdio discovered the exact seven tools and called listing through the
actual application/guard with a synthetic response. One request, response
cleanup and client cleanup completed. Memory sessions exercised all seven
consumers, strict validation, errors, partiality and cancellation. This was
the offline checkpoint before the separately approved S9.12 evidence below.
Official SDK source: https://github.com/modelcontextprotocol/python-sdk/tree/v1.30.0
documents v1.x maintenance/security support. Installed1.30.0 APIs were
inspected; no dependency update or latest-major claim.

### S9.12 real MCP acceptance — DEC-031

One-shot at2026-10-30T01:47:59Z, after explicit operator approval of one
page1/limit1 listing and memory-only configuration through the existing
loader. Generic ClientSession/stdio_client discovered exactly seven tools
and called list_products once with max_results1/page_size1/max_pages1.
Actual guarded POST /app-web/api/v2/produto/reduzidos body page1/limit1:
one attempt HTTP200, one received row and one returned item. Status partial,
error=null, complete_dataset=false. Exact projection/numeric strings/null/
absence compared in memory with the same response; structured/text JSON
equivalent. One response close, transport close and client close completed.
Original guards/TLS/identity/body/time limits and zero retries/redirects
remained active. Only safe structural counts/statuses/invariants persisted;
no source values, origin, credential or raw response retained.

G3 PASS and Sprint9 complete within this scope. This does not prove every
tool via real MCP, broad pagination, snapshot, deposit/freshness or absence
of undisclosed provider effects. No login/rotation/env write/mutation was
performed. Budget consumed and closed; no rerun or Sprint10 authorization.

## Sprint 8 — current application contract (DEC-029)

O3/O4/O5 were refreshed anonymously after browser hydration on 2026-10-29.
O5 still publishes idsProdutos/idsReduzidos arrays and retail/wholesale
source tables/amounts but no currency. O4 still describes physical minus
reservations and omission of idDeposito as selecting the configured user's
deposit; its idsReduzidos schema/example disagreement remains. O3 retains
page/limit and provider visibility restrictions. No Send action was used
while reading documentation. No official numeric quota or snapshot was found.

The approved option adds no HTTP filters: get_product_price selects exact
normalized product_id strings locally on prices; check_inventory selects
exact reduced_id strings locally on stock. Both accept identities1–256,
nonblank/no Unicode C, preserved exactly, and strict max_results1–1000,
default20/capped by configuration, counting all source rows. These are
bounded local lookups, not indexed/global queries. Errors/partiality take
precedence even when all rows are excluded. Existing DTO/Decimal/null/
missing-field and duplicate/conflict semantics remain unchanged.

Price retains source retail/wholesale tables and exact nominal amounts,
never discounts/final quote/table selection. currency defaults to null with
currency_unknown. A trusted caller may pass currency='BRL' based on the
maintainer's installation confirmation; currency_source explicitly says
operator_confirmation, not API evidence or currency conversion. Unsupported
currency inputs are rejected before HTTP. Missing both price values on any
matched record warns price_missing; identity found does not imply a quote.

Inventory adds inventory_scope: selection=configured_user_deposit,
deposit_id=null, branch_id=null, quantity_basis=physical_minus_reservations.
Scope/freshness warnings are explicit, item timestamp stays raw and local
retrieved_at is not freshness. No unit/availability/reservation/branch sum
is inferred; null quantity warns quantity_missing, never becomes zero.
No deposit lookup or idsReduzidos representation is chosen by analogy.

list_products(client, max_results=20, *, page_size=None, max_pages=1) starts
at page1, one page by default. Explicit max_pages1–100 is capped by config;
page_size must fit the effective row budget; None uses min(50,budget).
The collector's optional per-call max_pages=None preserves older callers,
validates before HTTP and never mutates shared limits. Partial/missing or
contradictory metadata, duplicates/conflicts, fixed sizes and source-row
budgets retain their previous semantics. provider_visible_catalog_only is
explicit; no initial-page/cursor/arbitrary filter or full ERP claim.

DEC-017's acceptance of official query intent and the inspected read paths
supports the no-reservation/movement design. It is not independent proof
of undisclosed server effects. Only existing POST reduzidos/precos/estoque
with page/limit are consumed here; auth/origin/TLS/guards, identity/1MiB,
deadlines, zero retries/redirects and shielded cleanup are unchanged.
All functions are application callables, not MCP registrations.

Offline: 16 new focused tests passed; full suite139 PASS/6.032s before
independent review; pip check passed. Independent application review
passed139 tests/5.999s. Three Important probe-only evidence defects were
reproduced and fixed before any send: record metrics before stopping,
accept a valid partial miss if the sample changes, and compare fidelity
against the current consumer response. Four synthetic probe regressions
passed after RED, followed by139 project tests/6.014s and pip check PASS.

Real S8.14: one-shot at23:25:50 UTC on2026-10-29, five page1/limit1
attempts, all HTTP200:2 prices (discovery + get_product_price),2 stock
(discovery + check_inventory),1 products (list_products). Five received
rows in total; each public consumer returned1 item, partial=true,
complete_dataset=false, error=null. Identity/projection, exact numeric
strings/null/absence were checked in memory against the same consumer
response; BRL operator context, scope, JSON and completed cleanup accepted.
Five response closes and client close completed. No raw/private values,
origins, credentials or arbitrary response keys were retained. No login,
rotation, mutation request, env change, retry or redirect. Budget exhausted
and closed. This is unitary sample evidence, not real multi-page/snapshot,
deposit identity/freshness or proof of undisclosed internal effects.

## Commercial code priority — PRD 1.5.0 / DEC-025

The operator uses product code/business SKU to mean the commercial code,
not necessarily the API codigoSku field. Prefer search_product_by_code
for that intent. Its source field is mascara, normalized as product_mask;
the existing sku/codigoSku projection and technical SKU lookup remain
distinct. No source-field renaming, fallback, persistent catalog, price/
stock join or MCP/conversational routing is introduced.

O3 was refreshed after browser hydration before this change. It documents
mascara:string as a product-mask filter in POST produto/reduzidos. It
does not state exact versus prefix equality. The client now accepts a
keyword-only product_mask only for products, string1–256/nonblank/no
Unicode C, passed unchanged as mascara with page/limit. It rejects use
with product_id, prices/stock or a generic filter dictionary. Defaults,
origin/Host guard, TLS, identity, bytes/deadlines, pagination and cleanup
remain unchanged. Exact equality is checked locally on the filtered
response; remote_product_code_exact_match discloses this behavior.
Errors/partiality take precedence over matching or empty items.

Real check started 18:41:47 UTC on 2026-10-29: exactly two authorized
products requests, both page1/limit20 with the supplied mascara string,
both HTTP200. The first checked fields in memory; the second exercised
actual search_product_by_code. One record matched mascara; zero matched
codigoSku/idProduto/idReduzido. The API SKU was null/absent in this sample.
The public function returned one exact match, found, partial=false,
complete_dataset=true for the filtered traversal, error=null; JSON and
client cleanup completed. No code, identity, description, amount, private
origin, token or raw response was persisted. The two-send probe is closed.

This confirms the supplied commercial code's source field, not universal
SKU equivalence or the provider's exact filter semantics for every input.
Technical codigoSku still lacks its own real acceptance sample. At that
checkpoint S7.11 remained open; later DEC-027 explicitly revised its
acceptance criterion and closed the sprint with that known exception.
No Sprint 8/9 started and no real SKU success is claimed.

## Historical decision and scope before DEC-029

G0/G1 evidence covers products/page-limit and bounded local searches. DEC-024 admits the products-only integer ID filter; DEC-025 additionally admits the mutually exclusive products-only mascara string filter and exact local commercial-code selection. Each has its own completed bounded real observation, not release by association. Exact EAN was observed; technical SKU still lacks real acceptance. Under DEC-017, the maintainer accepts O3/O4/O5 as evidence of intended query semantics, not proof of no internal effects. GET is not a prerequisite; commercial mutation remains prohibited. No MCP tool, other filter or general price/stock consumer is released. DEC-026 enriches the existing product DTO, not price/stock transport or Sprint8.

Bounded S5.01 field observations covered the three method/path pairs below, each page=1/limit=1 on 2026-10-29. The current allowlist has closed page/limit bodies; products may additionally use either idsProdutos=[validated integer] or validated mascara, never both. All completed observation budgets, including DEC-026's 100-row prefix, are exhausted, not ongoing request or registration permission. Existing token/loader was used without credential disclosure or login. This checkout remains NOT_READY, not FOUNDATION_READY or V1_COMPLETE.

| Candidate method | Literal path | Evidence | Policy status |
|---|---|---|---|
| POST | `/app-web/api/v2/produto/reduzidos` | L2, O3, S5.01, S6.13, S7.11, DEC-025/026 observations | BOUNDED_TEXT_ID_EAN_MASK_OBSERVED; named profile partial for six extras; technical SKU proof pending; no MCP registration |
| POST | `/app-web/api/v2/produto/precos` | O5 and S5.01 observation | FIELD_OBSERVED; no general/tool release |
| POST | `/app-web/api/v2/produto/estoque` | L2, O4 and S5.01 observation | FIELD_OBSERVED; no general/tool release |

The seven auxiliary Product queries remain INVENTORIED_ONLY, outside this narrow admission. Login remains AUTH_ONLY, separate from the commercial list. New routes require an explicit scope decision and individual review; no wildcard or product-prefix authorization is permitted.

The internal transport selects the operation and validates a closed typed filter schema, rejecting unknown fields and arbitrary tool-supplied bodies. Do not accept method, route, URL, headers, credentials or tenant through MCP arguments. POST query retries default to zero, including ambiguous timeouts; disable automatic commercial redirects (including same-origin 301/302/303/307/308), method rewriting and GET/POST fallback. Retry enablement requires specific repeat-safety evidence and a bounded policy, not an assumption from a query label.

The inventory covers all ten queries visible under the official Product reference and the separate authentication operation. Other API domains (orders, finance, customers, etc.) are outside the investigation and authorization scope. Public documentation evidence does not prove installation-specific permissions, runtime behavior, or absence of business side effects.

## Evidence types and sources

- L1: supplied local legacy source, `config.py:1-12`: dotenv and environment variable lookups for `TOKEN_NETONE`, `REDUCED_PRODUCTS_URL`, `STOCK_URL`.
- L2: supplied local legacy source, `integrations/netone.py:1-89`, inspected as text with URLs redacted before display. The local project identity and absolute path are intentionally omitted. No legacy code was imported or executed.
- O1–O19 below: rendered official Stoplight pages, read on 2026-10-27. Operation paths below include the published `/app-web/api/v2` prefix, without installation hosts.
- P: proposed NetOne MCP policy, not provider behavior and not implemented code.

| Ref | Official source | Observed evidence |
|---|---|---|
| O1 | [Quick start](https://net1ti.stoplight.io/docs/erp-api-v2/ZG9jOjQ3ODQzMw-guia-rapido) | Documentation navigation; test token guidance |
| O2 | [Authentication](https://net1ti.stoplight.io/docs/erp-api-v2/ZG9jOjc3MjM1NjU-autenticacao-no-sistema) | User token in `netone-auth-token`; ERP retrieval or API login; integration-enabled user required |
| O3 | [Reduced products](https://net1ti.stoplight.io/docs/erp-api-v2/1eefaa8cb7cc6-busca-reduzidos) | POST; product filters, response fields, paging; all ten Product menu entries labelled POST |
| O4 | [Stock](https://net1ti.stoplight.io/docs/erp-api-v2/47f2f0f5255d2-busca-estoque) | POST; stock = physical minus reservations; deposit selection |
| O5 | [Prices](https://net1ti.stoplight.io/docs/erp-api-v2/79683209728d7-busca-precos) | POST; retail and wholesale fields |
| O6 | [Login](https://net1ti.stoplight.io/docs/erp-api-v2/521ce3b9e03e9-realizar-login) | POST; required `usuario`, `senha`; 200/400/401 responses |
| O7 | [Response models](https://net1ti.stoplight.io/docs/erp-api-v2/ZG9jOjc3MjM1NjY-modelos-de-response-da-api) | Query envelope and errors, generally HTTP 400 or 500 |
| O8 | [Error schema](https://net1ti.stoplight.io/docs/erp-api-v2/c2NoOjQ5ODQ0MQ-response-error) | `erros[]` with `codigo`, `mensagem` |
| O9 | [Paged request schema](https://net1ti.stoplight.io/docs/erp-api-v2/r45eyxyy0430d-page-request-consulta) | `ultimaAlteracaoTimestamp`, `page`, `limit`; no numeric ceilings |
| O10 | [Product schema](https://net1ti.stoplight.io/docs/erp-api-v2/ac3fba80a0f19-produto) | Integer IDs, textual codes, retail/wholesale price fields |
| O11 | [API endpoints](https://net1ti.stoplight.io/docs/erp-api-v2/ZG9jOjc3MjM1Njg-endpoints-da-api) | Per-company production origin; test availability/data not guaranteed |
| O12 | [Reduced-product implementation article](https://net1ti.stoplight.io/docs/erp-api-v2/ZG9jOjc3MjM1Njk-implemente-a-busca-dos-reduzidos) | Incremental synchronization advice, not an alternative GET contract |
| O13 | [Collections](https://net1ti.stoplight.io/docs/erp-api-v2/a6fdd04bd3e3c-busca-colecoes) | POST `/colecao/todos` |
| O14 | [Deposits](https://net1ti.stoplight.io/docs/erp-api-v2/85a2f724527bf-busca-depositos) | POST `/deposito/todos` |
| O15 | [Categories](https://net1ti.stoplight.io/docs/erp-api-v2/umnkymd0e3z2a-busca-categorias) | POST `/categoria/todos` |
| O16 | [Classifications](https://net1ti.stoplight.io/docs/erp-api-v2/1d9265d543b35-busca-classificacoes) | POST `/classificacao/todos` |
| O17 | [Classification items](https://net1ti.stoplight.io/docs/erp-api-v2/1cb92b918d916-busca-itens-das-classificacoes) | POST `/classificacao/item/todos` |
| O18 | [Price tables](https://net1ti.stoplight.io/docs/erp-api-v2/r45vrrxlulq7j-busca-tabelas-de-preco) | POST `/preco/tabelas` |
| O19 | [Price-table items](https://net1ti.stoplight.io/docs/erp-api-v2/3e4ena76r1l46-busca-itens-de-uma-tabela-de-preco) | POST `/preco/itens` |

The extraction tool was unavailable for URL extraction; rendered browser access succeeded without login. Some immediate post-navigation reads contained only navigation, so pages were reread after content hydration. No accessibility restriction prevented reading the contracts listed here. No authenticated validation or supplier confirmation was available. The docs' test host and historical HTTP test address are not approved production configuration; no such host was contacted by the investigator.

## Legacy evidence

| Location | Observation | Limits of the evidence |
|---|---|---|
| L1 `config.py:1-12` | Environment loading and token/resource URL names | Does not prove token issuance, URL safety or permissions |
| L2 `integrations/netone.py:10-13` | Header `netone-auth-token` plus JSON content type | No OAuth or refresh code in the inspected integration |
| L2 `:16-48` | `requests.post(REDUCED_PRODUCTS_URL, json={page, limit}, timeout=30)`; page starts at 1, limit 50; `raise_for_status()`, JSON, `totalPages`, `result` | No explicit 200 check or specialized 401/403/429 handling; no total-page cap |
| L2 `:51-89` | Batches of 100 `idReduzido`; POST `STOCK_URL` with `idsReduzidos`; timeout 60; `raise_for_status()`; reads `result[].idReduzido` and `quantidade` | Batch 100 is a local implementation choice, not a documented provider maximum; no paging in this function |
| L2 `:44,87` | Progress uses `print()` | Must not be copied into MCP stdout |

No route was recovered from private environment values. The neutral `.env.example` paths are placeholders; official O3/O4 independently document the corresponding relative routes. The legacy integration contains only the two commercial calls above. It does not establish an independent GET by ID, EAN or price endpoint.

## Endpoint inventory

All commercial rows below are OFFICIALLY DOCUMENTED / NOT RELEASED FOR MCP. The first three rows have the bounded S5.01 field observation below, not general operational release; auxiliary rows are INVENTORIED_ONLY. "Documented" alone describes a published contract, not a successful call. Authentication header policy comes from O2 even where an operation page omits its security widget. No raw response examples from a commercial installation are included.

| ID / source | Method and literal path | Request body / documented response | Potential consumer (not registered) |
|---|---|---|---|
| reduced_products / L2, O3 | POST `/app-web/api/v2/produto/reduzidos` | `ultimaAlteracaoTimestamp`, `idsReduzidos: array[number]`, `idsProdutos: array[number]`, `mascara: string`, `carregarClassificacoes: boolean`, `carregarCategorias: boolean`, `page`, `limit`; 200 envelope with product array, `total`, `page`, `totalPages`, `totalElements` | `search_products`, details, code lookups, list/catalog analysis |
| product_prices / O5 | POST `/app-web/api/v2/produto/precos` | Timestamp, product/reduced-ID arrays, `mascara`, `page`, `limit`; 200 envelope with IDs, SKU, retail/wholesale table/value/discount fields | `get_product_price` |
| product_stock / L2, O4 | POST `/app-web/api/v2/produto/estoque` | `idDeposito`, `idsReduzidos` (schema/example conflict below), `codigoSku`, `comAlteracaoDesdeTimestamp`, `page`, `limit`; 200 envelope with IDs, `quantidade`, mask, color, size, SKU, timestamp | `check_inventory`, inventory analysis |
| collections / O13 | POST `/app-web/api/v2/colecao/todos` | `ultimaAlteracaoTimestamp`; 200/400; `result[]`: ID, descriptions, active flag, year, timestamp; `total` declared string | No current dedicated tool |
| deposits / O14 | POST `/app-web/api/v2/deposito/todos` | Timestamp, page, limit; 200/400; deposit ID, company code, code, name, start date, inventory-validation flag, timestamp; paging metadata | Inventory scope research only |
| categories / O15 | POST `/app-web/api/v2/categoria/todos` | Timestamp, page, limit; 200/400; ID, description, parent ID, timestamp; paging metadata | No current dedicated tool |
| classifications / O16 | POST `/app-web/api/v2/classificacao/todos` | Timestamp, page, limit; 200/400; ID, code, description, timestamp; paging metadata | No current dedicated tool |
| classification_items / O17 | POST `/app-web/api/v2/classificacao/item/todos` | Timestamp, page, limit, `classificacaoId`; 200/400; ID, code, description, classification ID, timestamp; paging metadata | No current dedicated tool |
| price_tables / O18 | POST `/app-web/api/v2/preco/tabelas` | Timestamp, page, limit; 200/400; table ID, company code, code, description, type, active flag, timestamp; pagination completeness not established by displayed response | Price table context research only |
| price_table_items / O19 | POST `/app-web/api/v2/preco/itens` | Required `tabelaPrecoId`; optional `produtoId`, `reduzidoId`, timestamp, page, limit; 200/400; item/table/reduced IDs, product mask, color, size, `preco`, timestamp | Price context research only |
| user_login / O2, O6 | POST `/app-web/api/v2/auth/login` | Required strings `usuario`, `senha`; 200 returns `token`, `mensagem`, `status`; 400/401 listed | Internal client authentication only, never an MCP tool |

No method/path for GET-by-ID, GET-by-EAN, GET-by-SKU, GET-price, GET-stock or GET-pagination was found. The POST filters do not establish text-description search, EAN filtering or exact-match GET support. No speculative GET route was requested, including OPTIONS/HEAD probes.

### Authentication boundary

O2 documents a token per ERP user, usable from the user's ERP integration settings or obtained through O6. Regeneration invalidates the old token. This establishes reusable user-token authentication, not an everlasting token or a known expiry policy. The existing token obtained successful responses for the three bounded S5.01 queries; account permission granularity and token lifetime were not established.

`TOKEN_NETONE` is the existing environment name observed in L1. `LOGIN_NETONE` and `SENHA_NETONE` exist in the local example but do not implement login. Sprint 3 configures the provided token in the private client's `netone-auth-token` header without sending a request. A future explicit token-login implementation must remain internal to `client.py`, use only the documented authentication route, and must not imply approval for commercial requests. Commercial query POST candidates have separate per-operation gates. No login, token rotation, OAuth grant or refresh is authorized by this document revision. OAuth, refresh tokens, token lifetime and least-privilege permission granularity remain unconfirmed.

The authentication article specifies `netone-auth-token`; generated examples on O3/O5 instead label a header `Token de Autenticação`. Do not copy that generated label as a wire-header contract. O2 and legacy agree on `netone-auth-token`, which was used successfully for the three S5.01 queries. This establishes compatibility for those requests, not every account permission or anonymous access. O4's displayed request sample omits an auth header; omission does not establish anonymous access.

Sprint 3 authentication review, 2026-10-28 (PRD 1.1.2): O2 was read again anonymously in the rendered browser after content hydration. It still states that the user token must be sent in `netone-auth-token`, can be retrieved from ERP user settings or obtained through `/auth/login`, requires an integration-enabled user, and is invalidated by regeneration. It does not establish OAuth, refresh or token lifetime. No Send action, login or ERP endpoint was invoked. Generic URL extraction was unavailable (search-only backend); browser reading supplied the actual article body. HTTPX SSL, timeout and logging documentation was also read through anonymous HTTPS; implementation options were checked against installed HTTPX 0.28.1. See the runbook for offline evidence, not authenticated provider responses.

### Pagination, fields and semantics

- O3/O4/O5 document `page` default 1 and numeric `limit`. O9's zero-valued example is not evidence that page 0 is valid. Numeric ceilings, limit default, termination behavior, maximum IDs per batch, requests/minute and concurrency are not established.
- Core query schemas show `ultimaAlteracaoTimestamp`, `total`, `result` and paging fields, but examples can omit paging fields. Requiredness, empty-result behavior and stable snapshot guarantees need clarification; do not synthesize missing totals.
- O3/O5 return only ecommerce-active reduced products with prices in at least one seller-configured price table. A complete paginated response need not represent the entire ERP catalogue.
- Product IDs are documented integers; masks, EAN and `codigoSku` are textual. `mascara` is the product mask/code, not proven equivalent to the reduced-product `codigoSku`. Preserve these distinct source fields; DEC-003 remains open for uniqueness and normalization.
- `codigoSku` may be null; published product examples also contain null EAN/prices. Examples illustrate possible values, not a complete nullable/required schema. Missing values stay null, never zero.
- O3/O5 describe `valor` as retail price and `valorAtacado` as wholesale price, with separate table descriptions and discounts. Currency, tax, final discount application and operator table choice are not established. Monetary parsing uses Decimal without a float intermediate, serializes values as strings and retains table provenance.
- O4 defines stock as physical minus reservations, not physical stock alone. `idDeposito` selects a deposit; omission uses the user's configured deposit. Actual deposit/company identity, aggregation, negative stock semantics and freshness remain unknown. Reading about reservations does not prove that a candidate query cannot create reservations; its HTTP method does not settle the question.
- Stock `idsReduzidos` is rendered as `number`, while its request example and legacy use an array. Do not silently choose a schema; obtain provider clarification.
- O12 uses `ultimaDataAlteracaoTimestamp`, while operation contracts use `ultimaAlteracaoTimestamp`; O4's filter is `comAlteracaoDesdeTimestamp`. Do not normalize these differing names into a guessed common API parameter. Synchronization/storage advice in O12 is outside the product scope.

### Errors, rate limits and payload bounds

O7 describes non-200 errors, generally 400/500; O8 defines `erros: [{codigo, mensagem}]`. O6 explicitly lists 200/400/401. Core commercial pages display 200, auxiliary pages 200/400. The investigator did not trigger any error. 403/404/429, Retry-After behavior, timeout budgets, retry safety, payload ceilings and per-route quotas are not verified provider contracts. Their handling is implemented as a local defensive policy, not an observed provider contract. Legacy `raise_for_status()` alone does not establish safe classification or redaction.

## Sprint 5: internal normalized records and pagination (PRD 1.1.6)

DEC-019 authorized the complete offline Sprint 5 slice, not only pagination. It did not authorize real requests, MCP tools, new filters or Sprint 6. O3/O4/O5/O10 were reread anonymously in the rendered documentation on 2026-10-28 after hydration; no Send action was used. Published examples contain omitted paging fields, null EAN/retail price and null last-change timestamps. O5 publishes an offset-bearing timestamp example, but this does not establish every record's temporal semantics. S5.01 was subsequently completed through a separate explicit authorization and the real observations below, not inferred from published examples.

`catalog.py` defines frozen `CatalogRecord` and `QueryResult` models, consumed by `NetOneClient._collect()` in `client.py`. They are internal components, not registered tools. The existing `_query()` remains the only request path: the same three literal POST routes and closed integer page/limit body, fixed origin, TLS, identity encoding, response-byte bound, no redirects/retries/fallback. No source field is interpreted as an instruction.

### Normalization and serialization

DEC-020 originally limited the projection to fields consumed in the legacy reference plus technical SKU/retail table provenance. DEC-026 now adds subgroup, notes, wholesale price/table and source block flag for the actual application-function output; see the linked priority contract above. mascara remains product_mask, distinct from codigoSku. Photos, color, size, discount application and arbitrary raw fields remain excluded. Reference persistence, destructive trimming and unrestricted loops are not reused; it was inspected as text, never executed.

| Source field | Normalized projection | Rule |
|---|---|---|
| idProduto / idReduzido | product_id / reduced_id | Nonnegative integer becomes its exact decimal string; nonempty textual IDs up to 256 characters are preserved, including leading zeros. Floats/bools rejected. Reduced ID required; product ID required for products/prices, nullable for stock. These are local compatibility rules, not proof of provider uniqueness or string-ID support. |
| mascara / codigoSku / ean | product_mask / sku / ean | Strings retained exactly, including leading zeros, whitespace and punctuation; no numeric coercion or mask/SKU substitution. Missing/null stays null. |
| descricao / grupoDescricao / linhaDescricao | description / group / line | Text preserved without trim, case folding or whitespace collapsing. |
| valor | price | Finite Decimal, or int converted exactly to Decimal; no float intermediate, numeric-string repair, discount application, currency assumption or table selection. |
| tabelaPreco | price_table | Preserve returned retail table description; no invented ID, currency or precedence. |
| subgrupoDescricao / observacao | subgroup / notes | Optional exact text; whitespace/null/absent preserved. Notes are data, not instructions. |
| tabelaPrecoAtacado / valorAtacado | wholesale_price_table / wholesale_price | Exact optional text / finite Decimal or exact int; JSON amount string. Product-source provenance, not a final quote or new prices consumer. |
| bloqueado | blocked | Strict bool or null; reject integer/string coercion. False is filled; neither value establishes stock/sellability or changes matching/status. |
| quantidade | quantity | Decimal from the same exact numeric path, including negative or explicit zero; missing/null stays null. No stock aggregation, reservation, deposit or unit inference. |
| ultimaAlteracaoTimestamp | last_changed_raw | Preserve source string/null; no datetime parsing, epoch units, timezone, stock freshness or cross-record ordering inferred. Non-null values produce timestamp_semantics_unverified. |

Each record lists absent projected source keys in `missing_fields`; explicit null is not listed. The five DEC-026 additions expand output keys/missing_fields, not the full raw record. Images, color, size, dimensions, discounts, classifications and flags other than blocked remain unprojected. All keys remain present in JSON; populated business fields are emitted before null/blank, missing_fields last. Object-key order is presentation, not a consumer dependency or result ranking. Duplicate comparison still uses full received rows; invalid projected types/contradictory metadata reject an entire page with fixed invalid_response, never a raw payload diagnostic.

Call `as_json()` to serialize: Decimal values become strings (scientific notation may be retained for extreme exponents); null stays null, tuples become arrays. No monetary quantization occurs. `QueryResult` includes status, source=netone_api, retrieved_at (local UTC collection observation, not provider freshness), items, returned_count, partial, warnings, error (stable code or null), operation, pages_fetched, rows_received, total_pages, total_elements and complete_dataset. Examples used for verification are synthetic, never claimed as ERP results.

### Pagination and data universe

- `_collect(operation, *, page_size=None, max_results=None)` is private, starts at page 1, and uses one fixed limit throughout. Sprint 6 adds an optional per-call row budget (strict integer 1–1000), capped by configuration without shared-state mutation. Default page size is min(50, effective row budget), a local choice, not a provider quota; omitted budget preserves the prior default. Explicit page_size must fit that budget. No arbitrary filters or resume cursor are accepted.
- `NETONE_MAX_PAGES` and `NETONE_MAX_RESULTS` apply to the whole collection. The row budget counts received rows before deduplication. If the remaining budget cannot accommodate another full fixed-size page, stop partial instead of shrinking limit and potentially changing page offsets. This can leave unused row capacity. No page/result ceiling can be disabled by the caller.
- A whole-collection deadline uses four configured phase-timeout seconds, as does each request; response cleanup may add at most the existing one-second shielded allowance. No automatic POST replay or wait/retry is added for Retry-After.
- Require valid integer page/totalPages for a complete traversal; validate optional totalElements when present. Missing metadata stops as partial, even for a short or empty page. Explicit null/invalid/changing/contradictory metadata is invalid_response. No total is synthesized from `total`, whose semantics are not established, or from a page's length.
- An empty result is not_found only on the first page with consistent terminal page metadata. Any later empty page or a page adding only previously seen rows stops partial, including the advertised terminal page. An empty first nonterminal page is also partial. Page/result/deadline limits and failures cannot become successful empty catalogs.
- Full identical rows with the same (product_id, reduced_id) are deduplicated with duplicate_rows_removed. Different reduced IDs of the same product survive. Conflicting rows with the same identity are retained, warned as conflicting_rows_preserved, and the result remains partial; no arbitrary last-write-wins or quantity sum is performed.
- Error before usable data gives status=error; error after usable data gives partial with preserved records and a stable error code. HTTP 404 remains an endpoint error, not a valid empty product query. External cancellation propagates rather than returning fabricated completeness.
- complete_dataset refers only to the endpoint pages traversed without known conflicts/interruption. It does not assert a stable snapshot or the entire ERP catalog: the provider's ecommerce-active/price-table visibility restrictions still apply. Stock scope remains the configured user's deposit, not a verified deposit identity. No price/stock join or global analysis is implemented.

The bounded S5.01 samples below were accepted by the normalizer and first-page metadata validator. Whole-dataset compatibility, real multi-page traversal and all nullable/type variants remain unverified. Offline verification exercises the actual internal collection/request path with in-memory transport, not only a standalone normalizer. See the runbook for executed scenarios.

### S5.01 real field evidence — 2026-10-29

At 16:41:30 UTC, a one-shot managed-scratch probe loaded operator-approved
configuration in memory and called `_query()` once per operation, with
page=1 and limit=1. All three returned successful 2xx JSON envelopes and
one record each. The existing fixed-origin guard, verified TLS, identity
encoding, 1 MiB cap, deadlines and zero retries/redirects remained enabled.
No login or token regeneration was needed. Client cleanup completed.

Only the following allowlisted shape summary was retained. `absent` and
`null` differ; no IDs, descriptions, prices, quantities, timestamps,
origins, credentials or arbitrary response keys are reproduced.

| Source field | Products | Prices | Stock |
|---|---|---|---|
| idProduto | integer | integer | absent |
| idReduzido | integer | integer | integer |
| mascara | string | string | string |
| codigoSku | null | null | null |
| ean | string | absent | absent |
| descricao | string | string | string |
| grupoDescricao | string | absent | absent |
| linhaDescricao | string | absent | absent |
| tabelaPreco | string | string | absent |
| ultimaAlteracaoTimestamp | string | string | null |
| valor | decimal | decimal | absent |
| quantidade | absent | absent | integer |

For each envelope, page/totalPages/totalElements/total were present integers;
their values were not retained. `_page_metadata(envelope, 1)` and
`normalize_record(operation, row)` accepted all three samples. Decimal
describes exact JSON numeric parsing, not a string received from the ERP.
This completes S5.01 and, with existing offline evidence, Sprint 5. It
does not prove the full universe, snapshot consistency, cross-endpoint
identity, monetary currency, stock deposit identity, timestamp semantics,
or absence of undisclosed server effects. No joins or tools were added.

## Sprint 6: approved bounded local search contract

The maintainer approved local textual search, the implementation plan and
delegated execution. This approval is limited to the product query path;
it does not register an MCP tool or approve price/stock consumers. The
function is implemented and verified offline and through the real guarded
path below. Independent task and whole-change reviews passed without
Critical/Important findings; final regression and scope audit passed.

The current rendered O3 article was reread anonymously on 2026-10-29.
It documents POST `/app-web/api/v2/produto/reduzidos`, page (default 1),
limit, ID arrays, mascara, timestamp and classification/category flags.
It does not document a description/query text filter. Only page/limit
will be sent by Sprint 6. Other published filters remain unsupported by
the client; documentation is not an instruction to forward them.

The selected application interface is
`await tools.search_products(client, query, max_results=20)`, where client
is the existing trusted process-owned NetOneClient, not a model argument.
It returns JSON-compatible data without registering anything in MCP;
registration remains Sprint 9. The input contract is:

- query: a string of 1–200 characters before strip, nonempty after strip,
  without Unicode C-category characters (Cc/Cf/Cs/Co/Cn). Leading/trailing input
  whitespace is ignored for matching, not removed from source records.
- Local literal substring matching with casefold over description,
  product_mask and sku. No regex, accent folding, semantic search,
  exact-code claim, or undocumented ERP text filter.
- max_results: strict integer 1–1000, default 20, capped by configured
  NETONE_MAX_RESULTS. This is a received-row inspection budget, including
  nonmatches and duplicates, not a promise of that many matching items.
- Page size min(50, effective row budget), kept fixed throughout traversal.
  Existing page/deadline/response-size bounds still apply. These are local
  conservative ceilings, not provider quotas.
- Only POST `/app-web/api/v2/produto/reduzidos` with a closed JSON body
  containing integer page and limit; same token header, origin, guard,
  verified TLS, identity encoding, zero retries and no redirects/fallback.

The output retains QueryResult's projection and collection metadata.
items/returned_count describe matches; rows_received counts all inspected
source rows. A fixed local_text_search warning discloses local matching.
Completed collection gives found or not_found according to matches.
Incomplete/conflicting collection remains partial even without matches;
an initial collection error remains error. Errors after useful source rows
remain partial even if none of those rows matches. Empty matching items
never conceal authentication, permission, timeout or endpoint failures.
complete_dataset describes only the traversed, provider-visible endpoint
universe, not a full ERP catalog or consistent snapshot.

Per-operation prerequisite review: DEC-017 already accepts the official
query purpose with residual risk of undisclosed internal effects. S5.01
establishes successful product page/limit responses through the token and
verified TLS, accepted normalization and first-page metadata. Current
Python 3.14.3, installed dependency consistency and the 51-test offline
configuration/guard/secrecy/lifecycle suite were verified before Sprint 6.
Those facts support the approved bounded product-search implementation;
neither a clean install nor broad account permissions is a written G0/G1
prerequisite for this narrow operation. New filters, remote multi-page
behavior, the public search path and MCP registration are distinct checks.

### S6.13 real application-search evidence — 2026-10-29

After the controller independently reran all 74 offline tests and pip
check successfully, the managed-scratch probe started at 17:25:28 UTC.
It loaded private configuration in memory and issued exactly the two
authorized product requests, both page=1/limit=1. Both returned HTTP 200.
The first supplied a term in memory; the second was performed by the
actual tools.search_products function with max_results=1. No term,
identity, description, price, source timestamp, private origin, credential
or raw response was retained. No login or token regeneration occurred.

Observed application result: one fetched page, one received row, one
matching item, status=partial, partial=true, complete_dataset=false and
error=null. local_text_search was present, JSON serialization succeeded,
and normalized identity matched the discovery sample in memory. This is
the correct result for a budget-limited sample, not a full-catalog claim.
Response cleanup completed through the existing query path; client
cleanup completed before the probe reported success. Guard, TLS, identity,
byte/deadline caps, zero retries and no redirects remained enabled.

This validates the public application function on a real single-page
sample. Remote multi-page traversal, all nullable variants, negative
search results, error responses and snapshot consistency were not tested
against the installation; relevant partial/error cases have offline
transport-backed regression evidence. No remaining request budget or
ongoing agent authorization is inferred from this completed observation.

## Sprint 7: approved ID and exact-code lookup contract

The maintainer approved the [design](superpowers/specs/2026-10-29-sprint-7-design.md)
and [plan](superpowers/plans/2026-10-29-sprint-7.md), choosing remote ID
filtering plus bounded exact local SKU/EAN matching. This is application
functionality only; no MCP registration, persistent catalog, price/stock
join or later sprint is included. Implementation and independent task
reviews passed; operational evidence and remaining limitation follow.

O3 was refreshed anonymously in the rendered browser on 2026-10-29 after
checking that the request schema had hydrated. It still documents POST
`/app-web/api/v2/produto/reduzidos`, `idsProdutos: array[number]` described
as filtering product ID, and integer idProduto in response records.
codigoSku/ean are output strings, not documented request filters there.
mascara remains a separate code, not a proven SKU alias. No dedicated
GET-by-ID/SKU/EAN route was found or invented. Anonymous static extraction
provided only the page shell; it was not used as request-schema evidence.

Approved application contracts:

- get_product_details(client, product_id, max_results=20): strict integer
  product_id 0–9223372036854775807, no bool/subclass/string coercion;
  64-bit ceiling is defensive local policy, not a documented NetOne quota.
  Encode only as idsProdutos=[product_id] on the existing products POST.
  Return normalized fields for all received reduced variants of that
  product within the budget, not arbitrary raw JSON or a stock/price join.
  A mismatching normalized product_id rejects its entire page before
  records are accepted; do not hide an ignored filter as successful data.
- search_product_by_sku(client, sku, max_results=20): exact local equality
  against codigoSku/sku only, never mascara/product_mask or description.
- search_product_by_ean(client, ean, max_results=20): exact local equality
  against ean only. No unsupported request parameter or barcode checksum.
- Codes are strings of 1–256 characters, not whitespace-only and with no
  Unicode C-category characters. Validation does not transform input;
  case, significant spaces, punctuation and leading zeros matter.
- Existing strict max_results 1–1000/default20/config cap counts received
  rows, including nonmatches/duplicates, not a count of promised matches.
  Page, deadline, byte, precision and cleanup behavior remains binding.
- Codes use products with page/limit only and disclose
  local_exact_sku_search or local_exact_ean_search. They are not global
  remote code search. No match in a limited traversal is still partial.
  Initial errors remain error; later errors remain partial even when no
  item matches. Complete valid traversal alone supports not_found within
  the provider-visible endpoint universe. Text search keeps its existing
  substring/casefold behavior and local_text_search warning.

The new internal keyword-only product_id is permitted only for products,
not prices/stock. No caller-controlled filter dict, method, route, URL,
token, tenant, remote codigoSku/ean/mascara filter or extra flags are added.
The original guard, TLS, identity encoding, 1 MiB bound, deadlines,
fixed-size pages and zero redirects/retries remain required.

A separate authorization permits up to four products requests, each
page=1/limit=1: one discovery and at most one public-function call per
usable ID/SKU/EAN held only in memory. Missing/null/unusable codes do not
justify another discovery, invented operational success or automatic
replay. Persist only known counts/statuses/types/invariants, never source
values or credentials. The original S7.11 criterion stayed open without
each required real observation; DEC-027 later waived the missing technical
SKU observation as a sprint-closure blocker, not as operational proof.
The one-shot probe is closed; its
unused conditional SKU call cannot become an extra discovery or rerun.

### S7.11 bounded real observation — 2026-10-29

Started at 18:03:27 UTC after independent task reviews and the controller's
97-test PASS run. Exactly three guarded products requests were issued,
each page=1/limit=1; all returned HTTP200. First: discovery in memory.
Second: actual get_product_details with idsProdutos=[discovered integer]
and max_results=1. Third: actual search_product_by_ean with the discovered
code held only in memory and max_results=1. No IDs, codes, descriptions,
price, quantity, private origin, credentials or raw responses were retained.

Details returned one matching reduced record, status=found, partial=false,
complete_dataset=true for this filtered traversal, error=null. EAN returned
one exactly matching record, status=partial, partial=true,
complete_dataset=false, error=null and local_exact_ean_search. Both kept
the discovery identity and serialized to JSON. Response cleanup completed
through the existing request path; client cleanup completed before the
success report. Guard/TLS/identity/byte/deadline bounds and zero
retries/redirects remained enabled.

SKU was not queried: the only discovery sample had no usable codigoSku.
No mask substitution, invented term or extra discovery was attempted.
The implementation has synthetic exact-SKU coverage but no real SKU
observation; S7.11 was open under its original criterion. DEC-027 later
records explicit acceptance with this exception. None of this proves global catalog
coverage, a stable snapshot, all SKU/EAN variants, multi-page filtered
behavior, broad permissions or full V1/MCP readiness.

## Refactor transport and diagnostics (PRD 1.2.0)

The client builds a request with `build_request()` and sends it with `send(stream=True)`. It explicitly iterates the public `response.stream` AsyncByteStream protocol so the first `aclose()` starts inside its bounded AnyIO shield; it does not use `aiter_raw()` auto-close outside that shield or write `is_stream_consumed`/other HTTPX state. There is no new streaming abstraction. Identity encoding, the 1,048,576-byte raw body limit and exact JSON/Decimal parsing remain unchanged.

`_query()` validates filters and constructs the closed page/limit body. The request hook checks only method, origin, Host and literal route, rather than deserializing that body a second time. The hook remains mandatory and is not a general untrusted in-process body sandbox. Only trusted internal code can access the private HTTP client. Response and client cleanup are each cancellation-shielded and bounded to one second; timeout of a stalled close is not proof that resource release completed.

Each request and the whole collection have a local total deadline of four times the phase timeout. Retries remain zero regardless of legacy `NETONE_MAX_RETRIES`. No route, filter, tool, real-call authorization or catalog semantics changed.

The server formatter emits only `level=<...> component=mcp|httpx|httpcore|library code=<component>_diagnostic`, never `record.msg`, args, exception or stack. Existing handlers are normalized only for root and the relevant families; loggers are not disabled. Entrypoint configuration/client failures retain fixed safe stderr messages. LangChain/LangGraph pins were removed without uninstalling the existing environment; the five remaining direct pins are preserved. Final application-validation results belong in the coordinator's runbook record, not this inventory.

## Historical gate record and unblock request before DEC-029

Current decision: DEC-017 accepts query purpose with residual limitations; DEC-024/025 admit typed ID/mask filters and distinct exact-code consumers. Real ID/EAN/commercial-code observations succeeded; technical SKU proof remains absent. DEC-027 closes Sprint 7 by explicit maintainer acceptance with that exception, revising only S7.11's criterion. This is not full operational proof. Commercial MCP tools remain absent; no price/stock consumer, arbitrary filter, new ERP request or Sprint 8 work is authorized. V1 remains NOT_READY.

Owner: maintainer, with NetOne support where the contract is ambiguous. Required next evidence:

1. Review O3/O4/O5 and legacy call paths against the admitted method/path pairs. Confirm exact version, closed filter schema, account permissions and paging/batch/payload limits; distinguish official limits from conservative local ceilings. Do not require GET equivalents or infer undisclosed routes.
2. Record O3/O4/O5 and reviewed request paths as the accepted evidence of query intent, and the risk that server-internal effects are not explicitly guaranteed. The legacy has no explicit mutation request in the inspected functions, but cannot prove server behavior. Stop if evidence of commercial mutation appears; HTTP 200 alone is not evidence of semantic safety.
3. The observed header works for these three samples. Resolve remaining stock ID-array shape, timestamp spelling/semantics, price currency/table semantics and pagination completeness questions before consuming those unsupported capabilities.
4. The S5.01 bounded queries and sanitized evidence above are complete. Any further request needs its own authorized scope and security/configuration review. A validation call can precede tool release; it is not permission to expose a tool or scan the full catalog. No credential or real record belongs in this document.
5. Review the implemented internal literal allowlist and any future tool registration. Documentation alone does not release tools.

Historical policy (PRD 1.0.1, superseded): all commercial POSTs were prohibited and G0 was blocked for lack of GET. The maintainer subsequently selected narrowly scoped query POST admission and authorized document revision. PRD 1.1.0 now records that decision (DEC-013, ADR-15/16); it is not a generic POST exception, completed security review, runtime authorization or permission to start another sprint. No new remote evidence was obtained by this revision.
