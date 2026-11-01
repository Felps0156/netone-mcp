# Local development

## Requirements and support boundary

Use Python **>=3.14,<4**, one `.venv` at the repository root and the single
root `requirements.txt`. No database, Docker, Node, CI service, LangChain,
LangGraph or LLM key is needed. Existing environments must not be replaced
without owner approval. Invoke pip through the intended environment's Python,
not an unrelated `pip` or interpreter on PATH.

The current environment was inspected as Windows/root-.venv Python3.14.3.
All five direct versions match the manifest. Sprint13 separately verified a
clean temporary installation of this manifest on Windows/Python3.14.3 with195
tests and pip check passing; the temporary environment was removed and root
.venv preserved. Evidence is in the [runbook](runbook.md). macOS/Linux commands below are operator
recipes, not claims of tested platforms. A new installation, dependency
upgrade or environment replacement is an explicit operator action.

## Windows PowerShell

From the repository root, inspect an existing environment first:

```powershell
.\.venv\Scripts\python.exe --version
```

Only if `.venv` is absent, select a verified compatible interpreter:

```powershell
py -3.14 --version
py -3.14 -m venv .venv
```

If the launcher does not select a compatible runtime, use its verified
absolute executable path rather than lowering the requirement. Install only
when creating/configuring the installation intentionally:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -B -m unittest discover -s tests -v
```

Windows Git Bash can use `.venv/Scripts/python.exe` with the same arguments.
No shell activation is required when using explicit executable paths.

## macOS and Linux

From the repository root, inspect an existing environment:

```bash
./.venv/bin/python --version
```

Only if `.venv` is absent:

```bash
python3.14 --version
python3.14 -m venv .venv
```

Then, as an intentional setup action:

```bash
./.venv/bin/python -m pip install -r requirements.txt
./.venv/bin/python -m pip check
./.venv/bin/python -B -m unittest discover -s tests -v
```

If the named interpreter or its venv module is unavailable, install/provision
a compatible runtime through the operator's platform policy. Do not silently
create a second environment or switch to system/global pip.

## Configuration and stdio

Read [configuration](configuration.md) before launching production. The
neutral .env.example has an empty token and is intentionally non-operational.
Never copy it over an existing .env. The loader reads .env beside config.py,
then applies recognized process overrides; setting process variables does not
skip reading an existing root file. Offline tests substitute the reader or
supply synthetic Settings instead of relying on those overrides for isolation.

For a configured operator installation only:

```powershell
.\.venv\Scripts\python.exe server.py
```

```bash
./.venv/bin/python server.py
```

The process waits for an MCP client, not an interactive chat prompt. Use the
[generic launch configuration](../README.md#install-and-start) with absolute
Python/server paths and operator-controlled credential injection. The
`mcpServers` wrapper is a common client convention, not a universal MCP file
format; translate these command/args values to the chosen client's settings.
Startup/discovery sends no ERP request. tools/call requires a separately
authorized scope and may return commercial data to that client/model.

## Offline workflow and dependency policy

Use synthetic settings/responses and in-memory transport; do not invoke an
unoverridden loader, a real query or `server.py` against the installation as
an offline test. Existing unittest fixtures cover generic SDK stdio,
malformed protocol, exact eight-tool discovery, strict inputs, equivalent
JSON, bounded pagination, errors, fidelity and completed cancellation cleanup.
The stdio fixture forbids external HTTP sends and substitutes configuration.
Keep its diagnostic sentinels out of real installation data.

All direct packages are used: mcp for protocol/server/client tests; pydantic
for strict inputs/URL/SecretStr; httpx for transport; anyio for deadlines and
cleanup shielding; python-dotenv for noninterpolating parsing. Exact pins
are not a transitive lockfile or a security advisory audit. Avoid unnecessary
installs/upgrades and follow [attribution constraints](attributions.md).

English code/public docs, pt-BR PRD/plans, single quotes, useful type hints
and focused modules remain the conventions. No external formatter/type-checker
pass is claimed; preexisting long-line style debt remains. For behavior
changes, add a failing regression first. Update PRD checkboxes only with
actual acceptance evidence; mocks never become ERP acceptance.

Version-changing Git actions/publication require separate authorization.
Do not use worktree or commit helper scripts in an execution that forbids
Git. Public-source snapshots/diffs can audit a documentation-only change
without reading .git, .env, virtualenv or caches.
