# Configuration

Sprint 2 implements local configuration validation only. It does not validate credentials against NetOne, implement login, authorize HTTP operations, or release MCP tools. G0 remains BLOCKED. The configuration safety gate passes when valid settings load and invalid settings fail safely before stdio startup; this is not the complete G1 authentication/transport gate.

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
| `NETONE_TIMEOUT_SECONDS` | `15` | Integer 1–120 seconds; future transport budget |
| `NETONE_MAX_RESULTS` | `100` | Integer 1–1000; future result ceiling |
| `NETONE_MAX_PAGES` | `5` | Integer 1–100; future pagination ceiling |
| `NETONE_MAX_RETRIES` | `0` | Integer 0–3; future global ceiling, never permission to retry a query POST |
| `NETONE_LOG_LEVEL` | `WARNING` | `WARNING`, `INFO`, `ERROR`, `CRITICAL`; future diagnostic configuration; DEBUG is rejected until transport redaction is verified |
| `LOGIN_NETONE`, `SENHA_NETONE` | Ignored | Legacy names only; no login, refresh, OAuth or token regeneration is implemented |

Timeout, pagination, result and retry settings are validated but have no HTTP consumer yet. The log setting does not configure or enable third-party debug logging. Query POST retries remain zero without specific repeat-safety evidence and approval, regardless of the configured ceiling. Commercial redirects and method/route fallback remain prohibited under the PRD.

## URL validation and legacy migration

For a new installation, provide `NETONE_BASE_URL` and `TOKEN_NETONE`. The example host is deliberately non-operational; do not contact it or substitute the published test host as operational evidence.

For a legacy installation, keep its file untouched. When `NETONE_BASE_URL` is absent, the loader derives the HTTPS origin from either supported legacy resource URL. If both legacy URLs exist, they must agree. If an explicit base exists, all provided legacy URLs must match it as well. Optional variables may be absent, but explicitly blank URLs are rejected, not silently ignored.

The base permits only an empty path or `/`. Legacy paths must match literally, with no trailing slash or encoding. Hostnames are normalized to lowercase, default port 443 is omitted, and IPv6 literals are canonicalized before origin comparison. Ports must be 1–65535. Public IP literals and well-formed, multi-label ASCII hostnames are accepted. Private/non-global IP literals, single-label hosts, `.local`/`.localhost` names, malformed DNS labels, backslashes, percent encoding, control characters, non-ASCII URL characters, query delimiters and fragment delimiters are rejected. Use operator-approved ASCII/punycode names where appropriate.

Bracketed authorities are accepted only for supported IPv6 literals; IPvFuture is rejected rather than reinterpreted as DNS. This is lexical validation, not DNS resolution, DNS-rebinding protection, certificate verification or remote-origin approval. The operator must approve the configured destination. DNS/IP checks at connection time, TLS and redirects belong to the future HTTP client. Validating a resource URL does not register or activate that endpoint.

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
