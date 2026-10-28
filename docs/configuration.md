# Configuration

Sprint 2 implemented local configuration validation; Sprint 3 consumes the validated settings in a private, token-configured HTTP client managed by the MCP lifespan. Neither sprint validates credentials against NetOne, implements login, authorizes HTTP operations, or releases MCP tools. G0 remains BLOCKED. Offline configuration/client acceptance is not complete G1: remote credential validation and operator installation readiness remain BLOCKED.

## Loading and ownership

`config.load_config()` is the sole loader. It reads `.env` next to `config.py`, not relative to the current working directory. Importing modules does not load configuration. Settings are immutable and process-owned; MCP arguments cannot supply configuration. The entrypoint validates settings before starting the empty stdio server. No request is made during loading or startup.

The root file is parsed in memory using the pinned python-dotenv parser, with UTF-8 BOM support and without interpolation. It is never rewritten. Existing process variables take precedence, including an empty value (which is rejected where a value is required). `os.environ` is not modified. Missing `.env` is allowed when the process provides configuration. Unreadable files, malformed assignments and duplicate recognized keys fail with fixed errors. Unknown keys, including legacy login/password keys, are not retained in settings and cannot enable login.

Do not overwrite an existing `.env` with `.env.example`. Configure missing settings through the process environment or an operator-controlled launch configuration. Do not send secrets in chat, command-line arguments or client tool arguments.

## Variables

These are local project controls, not provider quotas or evidence of supported remote behavior.

| Name | Default | Accepted values / purpose |
|---|---|---|
| `NETONE_BASE_URL` | Derived from a supported legacy URL if absent | HTTPS origin, such as `https://example.invalid`; no API path, userinfo, query or fragment |
| `TOKEN_NETONE` | Required | Operator-supplied user token; 1–8192 printable ASCII characters, no whitespace; validated structurally, not remotely |
| `REDUCED_PRODUCTS_URL` | Optional | Legacy reference with exact path `/app-web/api/v2/produto/reduzidos` |
| `STOCK_URL` | Optional | Legacy reference with exact path `/app-web/api/v2/produto/estoque` |
| `NETONE_TIMEOUT_SECONDS` | `15` | Integer 1–120 seconds; HTTP connect/read/write/pool timeout per phase, not a total request deadline |
| `NETONE_MAX_RESULTS` | `100` | Integer 1–1000; future result ceiling |
| `NETONE_MAX_PAGES` | `5` | Integer 1–100; future pagination ceiling |
| `NETONE_MAX_RETRIES` | `0` | Integer 0–3; global ceiling reserved for reviewed operations; actual transport retries remain zero |
| `NETONE_LOG_LEVEL` | `WARNING` | `WARNING`, `INFO`, `ERROR`, `CRITICAL`; MCP diagnostic configuration; DEBUG remains rejected; HTTPX/httpcore raw logs are suppressed |
| `LOGIN_NETONE`, `SENHA_NETONE` | Ignored | Legacy names only; no login, refresh, OAuth or token regeneration is implemented |

Timeout is consumed by the private HTTP client. Pagination/result limits remain reserved for future approved operations. The retry ceiling never enables replay: the transport uses zero retries even with a larger configured ceiling. The log setting configures MCP diagnostics, not third-party debug/trace output. Commercial redirects and method/route fallback remain prohibited under the PRD.

## Private HTTP client and lifecycle

`server.create_server(settings)` binds one `NetOneClient(settings)` to each MCP lifespan. The lifespan context contains `netone_client` for future trusted internal consumers; it is not an MCP resource, tool or configuration endpoint. Importing application modules creates no HTTP client and reads no `.env`. `main()` loads configuration once before starting stdio. Normal exit, body exceptions and AnyIO cancellation close the client; `aclose()` shields cleanup against the SDK's cancellation scopes and is idempotent after successful closure. A lifecycle failure returns a fixed `client_error`, not success or a raw exception group.

The public client exposes only asynchronous context management, `aclose()` and `is_closed`. It offers no arbitrary request method or commercial query. Its HTTPX object is private; a request hook rejects every attempted send with `blocked_operation` before transport. No operational endpoint is enabled, including the three policy candidates. This total guard is not the future per-operation allowlist/schema implementation of Sprint 4.

The operator's token is configured only in `netone-auth-token`; no login, OAuth, refresh, expiry handling, token regeneration or MCP token input exists. The provided Settings must come from `load_config()`, not model/tool arguments. Settings and the private HTTPX object must never be serialized or logged.

TLS uses explicit certificate/hostname verification and the HTTPX default CA store. `trust_env=False` prevents implicit proxies, `.netrc` authentication and `SSL_CERT_FILE`/`SSL_CERT_DIR` overrides. No insecure-TLS or proxy override is exposed. Installations requiring a private CA or proxy need a separately reviewed configuration decision; do not bypass certificate validation. Redirects are disabled even for the same origin, retries are explicitly zero, and the pool is bounded to one connection/one keepalive. All four timeout phases use `NETONE_TIMEOUT_SECONDS`; read timeout bounds inactivity between chunks, not total response time. Whole-response deadlines, payload limits, status/JSON handling and approved query schemas remain future sprint work.

Before client construction, raw `httpx`/`httpcore` diagnostics are suppressed process-wide, including existing descendants and later descendants inheriting normal logger configuration. No caller-supplied hooks or trace extensions are supported. The hosting Python process is trusted: deliberately accessing private fields or reconfiguring descendant loggers afterwards can bypass application conventions and is not sandboxed. Safe application diagnostics remain on stderr; stdout remains MCP-only.

`create_server()` also takes ownership of root/MCP logging before constructing FastMCP. Existing root handlers are replaced by a stderr handler, and existing named MCP handlers propagate to that boundary. Its formatter emits only `mcp_diagnostic: Diagnostic details suppressed for security.`; it never renders the SDK message, arguments, validation input, exception or stack. This covers SDK calls to the root logger, which can otherwise log malformed MCP request/notification contents even at WARNING. The configured log level controls whether a record is emitted, not its raw content. The trade-off is intentionally reduced SDK diagnostic detail and replacement of inherited logging sinks in this dedicated stdio process. Fixed configuration/client errors retain their distinct codes. No protocol response or installed SDK file is modified.

These are offline implementation controls, not evidence of a TLS handshake, DNS/rebinding protection, provider permissions, token freshness or business-side-effect safety. No ERP request is performed during construction, startup or shutdown.

## URL validation and legacy migration

For a new installation, provide `NETONE_BASE_URL` and `TOKEN_NETONE`. The example host is deliberately non-operational; do not contact it or substitute the published test host as operational evidence.

For a legacy installation, keep its file untouched. When `NETONE_BASE_URL` is absent, the loader derives the HTTPS origin from either supported legacy resource URL. If both legacy URLs exist, they must agree. If an explicit base exists, all provided legacy URLs must match it as well. Optional variables may be absent, but explicitly blank URLs are rejected, not silently ignored.

The base permits only an empty path or `/`. Legacy paths must match literally, with no trailing slash or encoding. Hostnames are normalized to lowercase, default port 443 is omitted, and IPv6 literals are canonicalized before origin comparison. Ports must be 1–65535. Public IP literals and well-formed, multi-label ASCII hostnames are accepted. Private/non-global IP literals, single-label hosts, `.local`/`.localhost` names, malformed DNS labels, backslashes, percent encoding, control characters, non-ASCII URL characters, query delimiters and fragment delimiters are rejected. Use operator-approved ASCII/punycode names where appropriate.

Bracketed authorities are accepted only for supported IPv6 literals; IPvFuture is rejected rather than reinterpreted as DNS. This is lexical validation, not DNS resolution, DNS-rebinding protection, certificate verification or remote-origin approval. The operator must approve the configured destination. Sprint 3 configures certificate verification and disabled redirects but blocks all requests; connection-time DNS/IP controls and actual TLS validation remain unverified. Validating a resource URL does not register or activate that endpoint.

If existing URLs fail validation, leave `.env` intact. The authorized operator can provide corrected configuration through the process environment; override all conflicting legacy URL variables as well as the base when changing origin. Never downgrade HTTPS, guess a replacement path, silently repair a source value or disclose the rejected URL. Local inspection during Sprint 2 found that the current `REDUCED_PRODUCTS_URL` fails validation; no value or host was displayed, and no migration or request was attempted.

## Errors and secret handling

The entrypoint returns exit code 1 with a single English `configuration_error` message on stderr and no stdout when configuration is invalid. Messages contain fixed variable names and constraints only, never the rejected value, file contents, private URL or third-party exception text. Successful startup reserves stdout for MCP protocol messages.

Settings omit token and base URL from their repr; tokens use Pydantic `SecretStr`. This reduces accidental disclosure, but is not encryption or a serialization boundary: privileged application code can deliberately access fields. Never serialize Settings, dump the environment, log `get_secret_value()`, or return settings from an MCP tool.

## Safe local checks

On the existing Windows environment:

```powershell
.\.venv\Scripts\python.exe -c "from config import load_config; load_config(); print('Configuration valid')"
.\.venv\Scripts\python.exe server.py
```

The first command reports only success; if configuration is invalid, use the server entrypoint for its sanitized error without a traceback. Neither command authenticates remotely. Do not print the settings object or URL/token fields for diagnostics. See [the runbook](runbook.md) for executed manual scenarios and limitations. No automated tests or test fixtures are part of this project.
