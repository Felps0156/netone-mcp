# NetOne API capability evidence

Investigation and authorized policy revision date: 2026-10-27. PRD version: 1.1.0.

## Decision and scope

G0 = BLOCKED because business-side-effect assurance and authorized runtime validation remain pending, not because the documented queries use POST. The maintainer explicitly authorized the PRD 1.1.0 revision to allow narrowly scoped, documented query POST candidates while prohibiting all commercial mutation. GET is no longer a prerequisite. Neither an HTTP verb, an operation's name nor a successful response alone proves absence of business side effects.

Operationally approved commercial method/path pairs: none. Approved MCP commercial tools: none. Three method/path pairs are policy candidates for future review/implementation, not authorized requests or registered tools; see the table below. No ERP call, login, token regeneration, credential lookup, or Stoplight "Send API Request" action was performed during the investigation. Documentation was read anonymously. This checkout is NOT_READY, not FOUNDATION_READY or V1_COMPLETE. Sprints 1–3 subsequently added an empty stdio server, offline configuration validation and a private token-configured client whose requests are all blocked before transport; they did not release commercial operations or change this inventory's remote evidence.

| Candidate method | Literal path | Evidence | Policy status |
|---|---|---|---|
| POST | `/app-web/api/v2/produto/reduzidos` | L2 and O3 | ADMITTED_CANDIDATE; not operationally approved |
| POST | `/app-web/api/v2/produto/precos` | O5 | ADMITTED_CANDIDATE; not operationally approved |
| POST | `/app-web/api/v2/produto/estoque` | L2 and O4 | ADMITTED_CANDIDATE; not operationally approved |

The seven auxiliary Product queries remain INVENTORIED_ONLY, outside this narrow admission. Login remains AUTH_ONLY, separate from the commercial list. New routes require an explicit scope decision and individual review; no wildcard or product-prefix authorization is permitted.

Future transport must choose the operation internally and validate a closed typed filter schema, rejecting unknown fields and arbitrary tool-supplied bodies. Do not accept method, route, URL, headers, credentials or tenant through MCP arguments. POST query retries default to zero, including ambiguous timeouts; disable automatic commercial redirects (including same-origin 301/302/303/307/308), method rewriting and GET/POST fallback. Retry enablement requires specific repeat-safety evidence and a bounded policy, not an assumption from a query label.

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

All commercial rows below are OFFICIALLY DOCUMENTED / NOT RELEASED FOR MCP. The first three rows are ADMITTED_CANDIDATE under PRD section 10.5, not proven safe or authorized for real calls; auxiliary rows are INVENTORIED_ONLY. "Documented" describes a published contract, not a successful call. Authentication header policy comes from O2 even where an operation page omits its security widget. No row is operationally allowlisted or remotely validated. No response examples from a commercial installation are included.

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

O2 documents a token per ERP user, usable from the user's ERP integration settings or obtained through O6. Regeneration invalidates the old token. This establishes reusable user-token authentication, not an everlasting token or a known expiry policy. Required integration permission is documented; actual account access was not checked.

`TOKEN_NETONE` is the existing environment name observed in L1. `LOGIN_NETONE` and `SENHA_NETONE` exist in the local example but do not implement login. Sprint 3 configures the provided token in the private client's `netone-auth-token` header without sending a request. A future explicit token-login implementation must remain internal to `client.py`, use only the documented authentication route, and must not imply approval for commercial requests. Commercial query POST candidates have separate per-operation gates. No login, token rotation, OAuth grant or refresh is authorized by this document revision. OAuth, refresh tokens, token lifetime and least-privilege permission granularity remain unconfirmed.

The authentication article specifies `netone-auth-token`; generated examples on O3/O5 instead label a header `Token de Autenticação`. Do not copy that generated label as a wire-header contract. O2 and legacy agree on `netone-auth-token`; provider clarification/runtime proof is still needed before declaring installation authentication validated. O4's displayed request sample omits an auth header; omission does not establish anonymous access.

Sprint 3 authentication review, 2026-10-28 (PRD 1.1.2): O2 was read again anonymously in the rendered browser after content hydration. It still states that the user token must be sent in `netone-auth-token`, can be retrieved from ERP user settings or obtained through `/auth/login`, requires an integration-enabled user, and is invalidated by regeneration. It does not establish OAuth, refresh or token lifetime. No Send action, login or ERP endpoint was invoked. Generic URL extraction was unavailable (search-only backend); browser reading supplied the actual article body. HTTPX SSL, timeout and logging documentation was also read through anonymous HTTPS; implementation options were checked against installed HTTPX 0.28.1. See the runbook for offline evidence, not authenticated provider responses.

### Pagination, fields and semantics

- O3/O4/O5 document `page` default 1 and numeric `limit`. O9's zero-valued example is not evidence that page 0 is valid. Numeric ceilings, limit default, termination behavior, maximum IDs per batch, requests/minute and concurrency are not established.
- Core query schemas show `ultimaAlteracaoTimestamp`, `total`, `result` and paging fields, but examples can omit paging fields. Requiredness, empty-result behavior and stable snapshot guarantees need clarification; do not synthesize missing totals.
- O3/O5 return only ecommerce-active reduced products with prices in at least one seller-configured price table. A complete paginated response need not represent the entire ERP catalogue.
- Product IDs are documented integers; masks, EAN and `codigoSku` are textual. `mascara` is the product mask/code, not proven equivalent to the reduced-product `codigoSku`. Preserve these distinct source fields; DEC-003 remains open for uniqueness and normalization.
- `codigoSku` may be null; published product examples also contain null EAN/prices. Examples illustrate possible values, not a complete nullable/required schema. Missing values stay null, never zero.
- O3/O5 describe `valor` as retail price and `valorAtacado` as wholesale price, with separate table descriptions and discounts. Currency, tax, final discount application and operator table choice are not established. Future monetary parsing must use Decimal without a float intermediate, serialize as strings, and keep table provenance.
- O4 defines stock as physical minus reservations, not physical stock alone. `idDeposito` selects a deposit; omission uses the user's configured deposit. Actual deposit/company identity, aggregation, negative stock semantics and freshness remain unknown. Reading about reservations does not prove that a candidate query cannot create reservations; its HTTP method does not settle the question.
- Stock `idsReduzidos` is rendered as `number`, while its request example and legacy use an array. Do not silently choose a schema; obtain provider clarification.
- O12 uses `ultimaDataAlteracaoTimestamp`, while operation contracts use `ultimaAlteracaoTimestamp`; O4's filter is `comAlteracaoDesdeTimestamp`. Do not normalize these differing names into a guessed common API parameter. Synchronization/storage advice in O12 is outside the product scope.

### Errors, rate limits and payload bounds

O7 describes non-200 errors, generally 400/500; O8 defines `erros: [{codigo, mensagem}]`. O6 explicitly lists 200/400/401. Core commercial pages display 200, auxiliary pages 200/400. The investigator did not trigger any error. 403/404/429, Retry-After behavior, timeout budgets, retry safety, payload ceilings and per-route quotas are not verified provider contracts. Their handling remains a future MCP defensive requirement, not an observed API result. Legacy `raise_for_status()` alone does not establish safe classification or redaction.

## Gate record and unblock request

Decision date: 2026-10-27. Result: G0 BLOCKED (DEC-001, DEC-014), for pending business-side-effect assurance and operational validation. S0.11 remains unchecked under its revised semantic-safety criterion; no checkbox was completed by changing policy. Commercial tools and operational allowlist remain empty. Policy candidates can be studied or implemented offline only in a separately authorized sprint. Research and policy approval are not runtime acceptance.

Owner: maintainer, with NetOne support where the contract is ambiguous. Required next evidence:

1. Review O3/O4/O5 and legacy call paths against the admitted method/path pairs. Confirm exact version, closed filter schema, account permissions and paging/batch/payload limits; distinguish official limits from conservative local ceilings. Do not require GET equivalents or infer undisclosed routes.
2. Establish per-operation evidence that no business write, synchronization with mutation, reservation, price/inventory movement or other hidden business mutation occurs, through an explicit contract or technical provider confirmation plus source/request review. The legacy has no explicit mutation request in the inspected functions, but it cannot prove internal ERP behavior. Record evidence and its limits; a query label or HTTP 200 alone is insufficient.
3. Resolve auth-header rendering, stock ID-array shape, timestamp spelling, price currency/table semantics and pagination completeness conflicts above.
4. Only after security review, safe configuration/transport and explicit bounded-call authorization are available, perform a small query using the documented method and record date, method/path, sanitized status/schema/completeness and appropriate no-mutation evidence. A validation call can precede tool release; it is not permission to expose a tool or scan the full catalog. No credential or real record belongs in this document.
5. Review a future literal allowlist and actual tool registration. Documentation alone does not release tools.

Historical policy (PRD 1.0.1, superseded): all commercial POSTs were prohibited and G0 was blocked for lack of GET. The maintainer subsequently selected narrowly scoped query POST admission and authorized document revision. PRD 1.1.0 now records that decision (DEC-013, ADR-15/16); it is not a generic POST exception, completed security review, runtime authorization or permission to start another sprint. No new remote evidence was obtained by this revision.
