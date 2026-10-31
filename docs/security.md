# Security and read-only policy

## What the application enforces

Only three commercial query POST routes exist in the private client:

| Method | Literal path | Internally constructed body |
|---|---|---|
| POST | `/app-web/api/v2/produto/reduzidos` | Integer page/limit; optionally idsProdutos=[strict integer] OR mascara=validated string, never both |
| POST | `/app-web/api/v2/produto/precos` | Integer page/limit only |
| POST | `/app-web/api/v2/produto/estoque` | Integer page/limit only |

`_query()` validates the typed inputs and constructs the closed body.
The mandatory pre-transport hook checks method, exact configured origin,
Host and literal path without query/fragment/userinfo or encoded-path
substitutions. It is not an arbitrary-body sandbox against trusted code
that deliberately accesses the private HTTP client. No generic HTTP/SQL/
command tool, wildcard route or model-selected destination exists.
PUT/PATCH/DELETE and other POST/GET operations are not admitted. Login is
not implemented even though its separate route is documented externally.

Read-only is a semantic policy, not a synonym for GET. The maintainer
accepted official query descriptions and inspected request paths with a
residual risk of undisclosed provider-side effects. HTTP200 and advisory MCP
readOnly annotations cannot prove provider internals or repeat safety.
There is no reservation, stock movement, order or other commercial-write
request in the application. Stop if evidence contradicts intended query use.

## Configuration and secrets

- Only `load_config()` reads configuration explicitly; imports do not.
  Operator-owned process values override recognized root dotenv entries
  without interpolation, environment mutation or file rewriting.
- Settings are immutable; origin/token are excluded from repr and token
  uses SecretStr. This prevents accidental display, not malicious access or
  safe arbitrary serialization. Never dump Settings, environment or headers.
- Keep origin and credentials in operator-controlled process configuration.
  Do not paste secrets into chat, MCP arguments, examples or command lines.
  Preserve existing .env; never replace it with .env.example.
- Seven strict extra-forbid MCP schemas accept only commercial inputs and
  bounded limits. No tenant, URL, method, headers, credential or currency
  argument is available to the model.
- `.gitignore` excludes .env/.env.*, .venv, caches and logs, except the
  neutral .env.example. Ignore rules are not proof that secrets are absent
  from an index, Git history, backup or other private file. No Git/history
  inspection is part of this execution.

## Transport, bounds and cancellation

HTTPS certificate and hostname verification are mandatory. Operator-approved
private/single-label hosts are allowed, not automatically trusted. No DNS
rebinding defense or remote permission certification is claimed. HTTPX uses
trust_env=False, no inherited proxy/netrc/CA overrides, one connection and
one keepalive. There are zero redirects, retries or method/route fallbacks,
even for same-origin redirects, 429, Retry-After or timeouts. The validated
legacy retry option is discarded, not permission to replay POST.

The client requests identity encoding, rejects compressed success bodies,
limits raw response bytes to1,048,576 before parsing, rejects duplicate JSON
keys/nonfinite numbers and parses Decimal exactly. These controls do not
bound all internal library/network buffers. Phase timeouts and request/
whole-query deadlines coexist; pages and received rows are capped locally.
Per-call budgets/filters do not mutate shared settings. Missing/changing/
contradictory paging evidence cannot create a complete dataset.

External cancellation propagates. Response and client cleanup each have a
one-second AnyIO shield; expiration is bounded failure, not guaranteed
release. Tests observe completion of mock stream/transport closure rather
than only is_closed. This is offline evidence, not remote cleanup assurance.

## Data and diagnostics

Returned descriptions/notes are untrusted data, never instructions. The DTO
projects explicit commercial fields rather than returning arbitrary raw keys.
Authorized commercial fields intentionally remain in tool results; safe
logging is not a promise to remove every sensitive meaning from source text.
The operator must decide which client/model may receive those results.

stdout is exclusively MCP. The dedicated process owns root and relevant
MCP/HTTPX/httpcore stderr handlers: only fixed level/component/code events
are formatted, never third-party message/args/exception/stack. Application
errors are fixed safe diagnostics. Invalid arguments, unavailable tools and
unexpected failures never echo inputs. ToolInputError maps to invalid_arguments;
internal ValueError/serialization failure maps to tool_error. Cancelling
only a local SDK task is not a substitute for MCP notifications/cancelled.

Null stock is unknown, not zero. Nominal source prices are not final quotes;
currency, deposit/branch identity, freshness and parts compatibility are not
inferred. Partial misses are inconclusive. No sums across units/deposits or
global metrics from samples are offered.

## Evidence and publication limits

The [runbook](runbook.md) records offline checks and bounded historical
observations with exhausted budgets. Sprint13 adds a separately authorized
one-request real MCP listing with verified TLS and completed cleanup, and a
Windows clean installation; neither establishes ongoing credentials/access,
all-tool coverage, dependency vulnerability audit, Git/history secret audit
or a platform matrix. Only the allowlisted public files are reviewed;
private configuration/virtualenv internals are not searched for source data.
[Attributions](attributions.md) records the unresolved project-license choice.
V1 remains NOT_READY; source publication requires a separate owner decision
and checks. Documentation completion is not permission to publish or query.

## Suspected disclosure or unsafe behavior

Stop the affected client/process and do not resend an ambiguous query.
Report only fixed failure categories and bounded counts through a private
maintainer channel; never attach raw logs/settings/responses. The maintainer
owns incident assessment, source-history review and any provider credential
revocation/rotation. This project implements no automatic login, token
rotation, commercial rollback or remote mutation to resolve an incident.
