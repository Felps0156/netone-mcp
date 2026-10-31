# Licenses and attributions

## Project license: owner decision pending

The root/public-source review found no project LICENSE, COPYING or NOTICE
file. This work does not select a license, assert ownership or grant rights
to copy/redistribute the project's source. The maintainer must decide the
project's license and confirm authorship/rights before public distribution.
Documentation being suitable for a public audience is not legal clearance
or authorization to publish. This remains an explicit release limitation.

## Reference architecture

[SCSI reference audit](scsi-reference.md) records the pinned source revision,
source links, adopted ideas and rejected infrastructure. That audit states
that no upstream source code was copied into NetOne MCP. The present review
found imports of installed packages, not vendored upstream modules. This is
an architectural attribution and bounded source review, not a legal opinion
or an exhaustive provenance audit of Git history (which was not inspected).
If source/assets are copied later, review their exact license and retain
required notices before distribution.

## Direct dependencies

The following metadata was read from the installed root-.venv distributions
on2026-10-31, not inferred from a different/latest upstream release:

| Distribution and pinned version | License metadata | Actual production consumer |
|---|---|---|
| mcp1.30.0 | MIT | server.py, mcp_tools.py; generic SDK client tests |
| pydantic2.14.1 | MIT (License-Expression) | config.py, mcp_tools.py |
| httpx0.28.1 | BSD-3-Clause | client.py |
| anyio4.15.1 | MIT (License-Expression) | client.py deadlines/shielding |
| python-dotenv1.2.4 | BSD-3-Clause | config.py parser |

No direct dependency is unused, so requirements.txt is unchanged. Installed
versions match its pins and pip check verifies dependency consistency, not
license compatibility or absence of vulnerabilities. MIT/BSD package metadata
does not assign a license to this project.

For a source-only handoff that installs dependencies normally, retain this
reference and review the actual distribution notices as appropriate. For
bundles, wheels, copied sources or binary redistribution, inspect all included
direct/transitive artifacts and retain applicable copyright/license notices;
this table is not a substitute for their full license texts. No dependency
bundle, transitive-license audit, third-party source vendoring, license change
or publication was performed in Sprints12/14.
