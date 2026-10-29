# NetOne API capability evidence

Initial investigation: 2026-10-27. Current policy: PRD 1.3.0, 2026-10-29. Sprint 5 evidence and Sprint 6's completed bounded local-search contract are recorded below. Offline and real-call checks and independent reviews passed; both non-blocking review findings were corrected.

## Decision and scope

G0/G1 PASS only for products/page-limit and the approved bounded local-search implementation of Sprint 6. This scoped review uses accepted query intent, verified offline safeguards and real S5.01 token/TLS evidence, not a new undefined general-release gate. Under DEC-017, the maintainer accepts O3/O4/O5 as sufficient evidence of intended query semantics. The documentation does not explicitly guarantee absence of internal effects; that remains a residual risk, not proof of a write. GET is not a prerequisite and commercial mutation remains prohibited. No MCP tool is approved or registered; price/stock consumers and additional filters are not released by this decision.

Bounded remote field observations: all three method/path pairs below, each with page=1 and limit=1, on 2026-10-29. Approved MCP commercial tools: none. Under DEC-018 the three method/path pairs are implemented in an internal allowlist with only page/limit filters; this is not permission for ongoing requests or tool registration. The original investigation used anonymous documentation only; the subsequent explicitly authorized S5.01 observation used the existing token through the loader without displaying credentials or logging in. This checkout remains NOT_READY, not FOUNDATION_READY or V1_COMPLETE.

| Candidate method | Literal path | Evidence | Policy status |
|---|---|---|---|
| POST | `/app-web/api/v2/produto/reduzidos` | L2, O3, S5.01 and S6.13 observations | BOUNDED_LOCAL_SEARCH_VALIDATED; no MCP registration |
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

DEC-020 narrows the projection to the fields actually consumed in the legacy reference (`database/products.py:37–46`), with only the separate API SKU and retail table description added for identity/provenance. The reference calls its `mascara` column sku; this implementation preserves that code as product_mask and does not equate it to codigoSku. Photos, color, size, wholesale prices and discounts are deliberately excluded, even if upstream includes them. Reference persistence, destructive trimming, product-only conflict keys and unrestricted loops are not reused. The reference was inspected as text only, never executed.

| Source field | Normalized projection | Rule |
|---|---|---|
| idProduto / idReduzido | product_id / reduced_id | Nonnegative integer becomes its exact decimal string; nonempty textual IDs up to 256 characters are preserved, including leading zeros. Floats/bools rejected. Reduced ID required; product ID required for products/prices, nullable for stock. These are local compatibility rules, not proof of provider uniqueness or string-ID support. |
| mascara / codigoSku / ean | product_mask / sku / ean | Strings retained exactly, including leading zeros, whitespace and punctuation; no numeric coercion or mask/SKU substitution. Missing/null stays null. |
| descricao / grupoDescricao / linhaDescricao | description / group / line | Text preserved without trim, case folding or whitespace collapsing. |
| valor | price | Finite Decimal, or int converted exactly to Decimal; no float intermediate, numeric-string repair, discount application, currency assumption or table selection. |
| tabelaPreco | price_table | Preserve returned retail table description; no invented ID, currency or precedence. |
| quantidade | quantity | Decimal from the same exact numeric path, including negative or explicit zero; missing/null stays null. No stock aggregation, reservation, deposit or unit inference. |
| ultimaAlteracaoTimestamp | last_changed_raw | Preserve source string/null; no datetime parsing, epoch units, timezone, stock freshness or cross-record ordering inferred. Non-null values produce timestamp_semantics_unverified. |

Each record lists absent projected source keys in `missing_fields`; an explicitly null key is not listed. This is an explicit projection, not a full ERP product: images, color, size, wholesale/discount fields, dimensions, flags, classifications and other unprojected fields are not exposed or required. Duplicate comparison uses full received rows so differences outside the projection are not silently discarded. Source metadata is untrusted; strings are data, not commands. Invalid projected types or contradictory page metadata reject that entire page before records are accepted, with fixed invalid_response, never a raw payload diagnostic.

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

## Refactor transport and diagnostics (PRD 1.2.0)

The client builds a request with `build_request()` and sends it with `send(stream=True)`. It explicitly iterates the public `response.stream` AsyncByteStream protocol so the first `aclose()` starts inside its bounded AnyIO shield; it does not use `aiter_raw()` auto-close outside that shield or write `is_stream_consumed`/other HTTPX state. There is no new streaming abstraction. Identity encoding, the 1,048,576-byte raw body limit and exact JSON/Decimal parsing remain unchanged.

`_query()` validates filters and constructs the closed page/limit body. The request hook checks only method, origin, Host and literal route, rather than deserializing that body a second time. The hook remains mandatory and is not a general untrusted in-process body sandbox. Only trusted internal code can access the private HTTP client. Response and client cleanup are each cancellation-shielded and bounded to one second; timeout of a stalled close is not proof that resource release completed.

Each request and the whole collection have a local total deadline of four times the phase timeout. Retries remain zero regardless of legacy `NETONE_MAX_RETRIES`. No route, filter, tool, real-call authorization or catalog semantics changed.

The server formatter emits only `level=<...> component=mcp|httpx|httpcore|library code=<component>_diagnostic`, never `record.msg`, args, exception or stack. Existing handlers are normalized only for root and the relevant families; loggers are not disabled. Entrypoint configuration/client failures retain fixed safe stderr messages. LangChain/LangGraph pins were removed without uninstalling the existing environment; the five remaining direct pins are preserved. Final application-validation results belong in the coordinator's runbook record, not this inventory.

## Gate record and unblock request

Current decision: DEC-017 accepts query purpose with the residual limitation above. S5.01 and S6.13 supply real field/token/TLS and public-search evidence. The approved Sprint 6 design/plan authorized implementation and the completed two-request observation. G0/G1 PASS for products/page-limit only; commercial MCP tools remain absent, and no price/stock consumer or additional remote filter is released. Sprint 6 is complete with independent review and final regression/scope audit accepted.

Owner: maintainer, with NetOne support where the contract is ambiguous. Required next evidence:

1. Review O3/O4/O5 and legacy call paths against the admitted method/path pairs. Confirm exact version, closed filter schema, account permissions and paging/batch/payload limits; distinguish official limits from conservative local ceilings. Do not require GET equivalents or infer undisclosed routes.
2. Record O3/O4/O5 and reviewed request paths as the accepted evidence of query intent, and the risk that server-internal effects are not explicitly guaranteed. The legacy has no explicit mutation request in the inspected functions, but cannot prove server behavior. Stop if evidence of commercial mutation appears; HTTP 200 alone is not evidence of semantic safety.
3. The observed header works for these three samples. Resolve remaining stock ID-array shape, timestamp spelling/semantics, price currency/table semantics and pagination completeness questions before consuming those unsupported capabilities.
4. The S5.01 bounded queries and sanitized evidence above are complete. Any further request needs its own authorized scope and security/configuration review. A validation call can precede tool release; it is not permission to expose a tool or scan the full catalog. No credential or real record belongs in this document.
5. Review the implemented internal literal allowlist and any future tool registration. Documentation alone does not release tools.

Historical policy (PRD 1.0.1, superseded): all commercial POSTs were prohibited and G0 was blocked for lack of GET. The maintainer subsequently selected narrowly scoped query POST admission and authorized document revision. PRD 1.1.0 now records that decision (DEC-013, ADR-15/16); it is not a generic POST exception, completed security review, runtime authorization or permission to start another sprint. No new remote evidence was obtained by this revision.
