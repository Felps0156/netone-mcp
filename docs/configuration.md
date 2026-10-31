# Configuration

`config.load_config()` is the only loader. It explicitly reads `.env` beside `config.py`, overlays recognized process variables, validates settings, and makes no network request. Imports do not load configuration. `main()` loads once before stdio; `create_server(settings)` manages one private client per lifespan. No tool accepts URL, method, route, header, credential or tenant configuration.

## Loading and secret ownership

The pinned python-dotenv parser reads UTF-8/BOM in memory without interpolation or rewriting the file. Process values take precedence, including explicitly empty values, which fail where a value is required. `os.environ` is not mutated. A missing file is allowed when process settings suffice; unreadable files, malformed assignments and duplicate recognized keys fail with fixed diagnostics. Unknown keys and legacy login/password keys are not retained in settings.

Settings are immutable. URL/token are omitted from repr; token uses `SecretStr`. This is accidental-disclosure protection, not encryption or a serialization boundary. Never dump settings/environment, render a secret, or return configuration through MCP. Preserve an existing `.env` exactly: no display, overwrite, move or replacement by `.env.example`. Use an operator-controlled launch configuration for migration; never supply credentials through chat or command-line arguments.

## Variables

Local controls are not provider quotas.

| Name | Default | Accepted values / purpose |
|---|---|---|
| `NETONE_BASE_URL` | Derived from supported legacy URL if absent | Operator-approved HTTPS origin; no API path, userinfo, query or fragment |
| `TOKEN_NETONE` | Required | 1–8192 printable ASCII characters, no whitespace; structural validation only |
| `REDUCED_PRODUCTS_URL` | Optional | Exact path `/app-web/api/v2/produto/reduzidos` |
| `STOCK_URL` | Optional | Exact path `/app-web/api/v2/produto/estoque` |
| `NETONE_TIMEOUT_SECONDS` | `15` | Integer 1–120; timeout for each connect/read/write/pool phase |
| `NETONE_MAX_RESULTS` | `100` | Integer 1–1000; whole-collection received-row ceiling |
| `NETONE_MAX_PAGES` | `5` | Integer 1–100; whole-collection page ceiling |
| `NETONE_MAX_RETRIES` | `0`, legacy compatibility only | Validated integer 0–3, then discarded; never enables replay and is not operational state in Settings |
| `NETONE_LOG_LEVEL` | `WARNING` | DEBUG/INFO/WARNING/ERROR/CRITICAL under the same safe diagnostic boundary |
| `LOGIN_NETONE`, `SENHA_NETONE` | Ignored | No login, refresh, OAuth or token regeneration |

## URL validation and legacy migration

URL parsing uses a library rather than a public-network lexical allowlist. Require HTTPS, valid host/port and no embedded credentials, query or fragment. Base path must be empty or `/`; legacy paths match literally, without trailing slash or encoding substitutions. Origin comparison normalizes hostname case, default port 443 and IPv6 representation. All supplied base/legacy origins must agree. Optional URL variables may be absent, not explicitly blank.

Operator-defined private HTTPS addresses and single-label hosts are allowed. This does not approve a destination, resolve DNS, prevent DNS rebinding or establish a TLS handshake. Certificate/hostname verification remains mandatory; private addressing is not an insecure-TLS exception. Do not infer a new endpoint or repair malformed source configuration silently.

For a new installation, provide base and token. For a legacy installation, keep the file intact and derive origin from a valid supported URL if the base is absent. If changing origin through process configuration, override every conflicting legacy URL as well as the base. Neutral `example.invalid` hosts are non-operational; never probe them or the published test host as an installation check.

Historical Sprint 2 inspection found a local reduced-products route mismatch;
the operator later corrected configuration before the successful bounded
S5.01 observations. No value is published. This documentation execution has
not reread the installation file or established current readiness. The
historical mismatch is not a current diagnosed fault.

## Private client and request limits

The public client offers lifecycle/context management, `aclose()` and `is_closed`, not an arbitrary HTTP interface. Private `_query()` validates integer page/limit filters and constructs the closed body. Products accepts either keyword-only product_id (strict integer 0–9223372036854775807, local ceiling, encoded as idsProdutos singleton) or product_mask (string1–256/nonblank/no Unicode C, passed unchanged as mascara), never both. Prices/stock reject both product-specific filters; no generic dictionary is accepted. ID-filtered pages reject any unrelated normalized identity atomically. Mask-filter equality is not assumed from the provider: search_product_by_code selects exact product_mask values locally while retaining partial/error state. Its mandatory request hook checks only method, fixed origin/Host and one of the three literal POST routes in the [API inventory](api-capabilities.md), without deserializing the body a second time. Real calls require separate authorization; startup/shutdown do not query ERP.

Token goes only in `netone-auth-token`. HTTPX uses explicit certificate/hostname verification and its normal CA store, `trust_env=False`, no inherited proxies/netrc/CA overrides, no redirects, zero retries and one connection/keepalive. No caller-supplied transport/hooks/trace options are exposed. `Retry-After`, 429, timeout or a legacy retry setting never causes POST replay or method/route fallback.

Each request and the whole collection have a local deadline of four times the configured phase timeout. Response cleanup may add up to one second under an AnyIO cancellation shield. The client uses `build_request()` plus `send(stream=True)` and explicitly iterates the public `response.stream` AsyncByteStream protocol. It does not use auto-closing `aiter_raw()` outside the shield or write `is_stream_consumed`/other HTTPX state. Both response and client cleanup have a one-second shielded allowance, not an unlimited shield. Requiring `Accept-Encoding: identity` and rejecting compressed success responses avoids unbounded decompression before a size check. Count raw bytes, cap each body at 1,048,576 bytes, reject duplicate keys/nonfinite JSON, and require a JSON object with a `result` list. This does not bound underlying library/network buffers or prove provider compatibility.

The collector keeps page size fixed, default min(50, effective row budget), with whole-query page/row/deadline ceilings and conservative partiality. Its optional per-call max_results accepts strict integers 1–1000, capped by configured NETONE_MAX_RESULTS without mutating Settings or shared client state; omission preserves the configured default. Explicit page_size must fit the effective budget. Text, technical-SKU and EAN searches count all received rows, not only matches; their terms stay local. The priority commercial-code function uses only the documented mascara filter, still under that received-row budget. See [API contracts](api-capabilities.md#commercial-code-priority--prd-150--dec-025); ID/mask filters and budgets remain call-local. External cancellation propagates. Cleanup failure must not mask the original error/cancellation; stalled bounded closure is not proof of release, and HTTPX closed state alone is not cleanup evidence.

## Logging and errors

stdout is MCP-only. The dedicated process normalizes root and relevant MCP/HTTPX/httpcore handlers, emitting only `level=<...> component=mcp|httpx|httpcore|library code=<component>_diagnostic`. It does not indiscriminately disable loggers or render raw SDK/HTTP messages, arguments, validation input, exception text or stacks, including malformed MCP data and root DEBUG. Application-owned fixed/sanitized diagnostics may remain specific. Configuration/client failures retain safe codes; no SDK source or protocol reply is patched. A trusted embedding process can deliberately reconfigure private logging; this is not a sandbox.

Invalid configuration makes the entrypoint return exit 1, no stdout and a safe `configuration_error` diagnostic without rejected values. Structural configuration, mock HTTP and stderr checks are offline controls, not authentication, permissions, token freshness, DNS/TLS or no-business-side-effect proof.

## Safe offline checks

```powershell
.\.venv\Scripts\python.exe -B -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m pip check
```

Tests must use synthetic settings and in-memory file/transport substitutions, never the real `.env` or ERP. Do not run an unoverridden `load_config()` as part of this refactor. [Runbook](runbook.md) separates historical evidence, the executed offline refactor checks and remaining operational validation.
