# Lore — Tribal Knowledge Archaeologist

> "DataHub knows what your data is. Lore knows why."

## What is Lore?

Lore is a multi-agent system that mines institutional knowledge from git
history, PR comments, and DataHub lineage patterns — then
synthesizes and writes that knowledge back to DataHub as structured,
evidence-linked, confidence-scored documentation. When a senior data
engineer leaves, everything they knew about *why* tables are structured the
way they are, why a column is always null on Tuesdays, why a pipeline has a
3am workaround, silently disappears. Lore captures it before it walks out
the door.

## Demo Video

_Add your demo video link here._

## The Problem It Solves

Data catalogs like DataHub are excellent at capturing **what** exists in a
data stack — schemas, lineage, ownership. They're silent on **why**. That
context lives in the heads of the people who built the pipeline, scattered
across old PR threads and commit messages nobody rereads. Lore
treats that scattered context as excavatable evidence, cross-references it,
and turns it into permanent, sourced documentation before the person who
knew it moves on.

## How It Works

```
                        ┌─────────────────────┐
                        │  Orchestrator Agent  │
                        └──────────┬───────────┘
                                   │ fan-out (parallel)
                    ┌──────────────┴───────────────┐
                    ▼                               ▼
             ┌─────────────┐                ┌───────────────┐
             │  Git Miner   │                │ DataHub Miner │
             │ commits, PRs,│                │   lineage /   │
             │ review       │                │   ownership   │
             │ comments,    │                │   anomalies   │
             │ code comments│                │               │
             └──────┬───────┘                └───────┬───────┘
                    └───────────────┬───────────────┘
                                   ▼
                        ┌─────────────────────┐
                        │   Synthesis Agent    │  (Groq LLM)
                        │  cross-references    │
                        │  evidence → why /    │
                        │  quirks / context    │
                        └──────────┬───────────┘
                                   ▼
                        ┌─────────────────────┐
                        │  Confidence Scorer   │
                        │  HIGH / MEDIUM / LOW │
                        └──────────┬───────────┘
                                   ▼
                     HIGH → write to DataHub (docs +
                            custom properties, evidence-linked)
                     MEDIUM → flagged for human review
                     LOW → surfaced only, not written
```

Progress streams to the frontend in real time over a WebSocket
(`/ws/excavation/{job_id}`) as each miner and the synthesis step complete.

## MCP Server Integration

The core pipeline above talks to DataHub via the `acryl-datahub` Python SDK
directly. The **Dependency Graph page's search bar** is a separate,
additive integration that goes through
[DataHub's official MCP Server](https://github.com/acryldata/mcp-server-datahub)
instead — a real client of DataHub's Model Context Protocol tools (`search`,
with relevance-based ranking across all connected platforms), not just the
SDK.

This lives in its own **fully isolated virtualenv** (`backend/mcp_bridge/`),
for a concrete reason: `mcp-server-datahub`'s dependencies require
`starlette>=0.49.1`, while this project's `fastapi==0.111.0` requires
`starlette<0.38.0` — confirmed by hand, there is no version of `starlette`
that satisfies both. Even the bare `mcp` client SDK pulls in the same
conflicting `starlette` requirement, so no part of the MCP client protocol
can share a process with the main backend. The main app spawns
`mcp_bridge/search.py` as a subprocess (using `mcp_bridge/.venv`'s own
Python interpreter), which itself spawns and talks to the real
`mcp-server-datahub` process over stdio — full process isolation end to
end. If this bridge isn't set up, the rest of the app is unaffected; the
search bar just reports itself unavailable.

Setup:
```bash
cd backend/mcp_bridge
python -m venv .venv
.venv/Scripts/activate   # Windows; use `source .venv/bin/activate` on macOS/Linux
pip install mcp-server-datahub
```

No further wiring needed — the main app finds this venv by relative path.

## Quick Start

```bash
# 1. Start DataHub
datahub docker quickstart
datahub datapack load showcase-ecommerce

# 2. Backend (isolated virtualenv — do not install into a global/shared Python env)
cd backend
python -m venv .venv
.venv/Scripts/activate   # Windows; use `source .venv/bin/activate` on macOS/Linux
pip install -r requirements.txt
cp ../.env.example .env  # Fill in your tokens
python main.py

# 3. Frontend
cd frontend && npm install && npm run dev
```

Backend runs at `http://localhost:8000`, frontend at `http://localhost:3000`.

## Running Tests

```bash
cd backend
pip install -r requirements-dev.txt
pytest
```

The backend test suite (`backend/tests/`) mocks every external dependency —
DataHub, GitHub, Groq — so it runs in a couple of seconds with no Docker,
tokens, or API keys needed. It's deliberately weighted toward the real bugs
found while building this (the "don't clobber existing docs" write-safety
logic, the pending-review status defaulting, the JSON-in-markdown-fence LLM
quirk, non-dataset lineage entities) rather than just exercising the happy
path.

## Environment Setup

See `.env.example` at the repo root (copy it into `backend/.env`):

| Variable | Purpose |
|---|---|
| `DATAHUB_GMS_URL` | DataHub GMS endpoint (default `http://localhost:8080` for local quickstart) |
| `DATAHUB_TOKEN` | Auth token for DataHub; leave empty for local no-auth setup |
| `GITHUB_TOKEN` | Personal access token with `repo` read scope, used by the Git Miner |
| `GITHUB_REPO_OWNER` / `GITHUB_REPO_NAME` | The repo Lore mines for commits, PRs, and code comments |
| `GROQ_API_KEY` / `GROQ_MODEL` | Groq API credentials for the Synthesis Agent (free tier) |
| `BACKEND_PORT` / `FRONTEND_PORT` | Local ports |

## A Note on Package Naming

The backend's DataHub integration code lives in `backend/datahub_integration/`
rather than `backend/datahub/`. Naming it `datahub` would shadow the
installed `acryl-datahub` SDK's own top-level `datahub` package once
`backend/` is on `sys.path` — any `import datahub.emitter...` from inside
that folder would resolve to itself instead of the real SDK. Renaming it
avoids that collision.

## Known Windows Issue: `datahub datapack load`

The `acryl-datahub` CLI (v1.7.0, current as of writing) has an unpatched bug
on Windows: its file-source loader uses Python's `urlparse()` to detect
whether a path is local, S3, HTTP, etc. `urlparse()` misreads a Windows
drive letter (e.g. `C:\Users\...`) as a URL scheme named `c`, so any local
file path lookup fails with `KeyError: 'Did not find a registered class for
c'`. This isn't specific to our setup — it will hit any Windows user running
`datahub datapack load` or ingesting local files via the file source. There
is no newer released version or config flag that fixes it.

The workaround is a one-line patch to
`.venv/Lib/site-packages/datahub/ingestion/fs/fs_base.py`: special-case
Windows drive-letter paths (`^[a-zA-Z]:[\\/]`) as `"file"` before falling
through to `urlparse()`, mirroring what `pathlib.Path.as_uri()` does
internally. Because this patches a file inside `.venv`, **it does not
survive recreating the virtualenv** — if you ever delete and reinstall
`backend/.venv`, reapply this patch (or check if upstream has fixed it by
then) before running any `datahub datapack load` / local file ingestion.

## Sample Outputs

See [`examples/`](examples/) for real shapes of what Lore produces — every
file is validated against the actual Pydantic response models, not just
hand-written to look plausible:
- `sample_output_payments_table.json` — a HIGH-confidence knowledge unit, auto-written to DataHub (`written_to_datahub: true`)
- `sample_output_churn_pipeline.json` — a MEDIUM-confidence unit; this is exactly the shape that lands in the **Pending Review** queue (`written_to_datahub: false`) until a human approves or rejects it
- `sample_risk_report.json` — a Knowledge at Risk dashboard payload across CRITICAL/AT_RISK/SAFE assets
- `sample_dependency_graph.json` — the whole-instance dependency graph (`GET /api/dependency-graph`) the frontend renders as an interactive graph
- `sample_asset_detail.json` — everything shown for one asset (`GET /api/asset-detail/{urn}`) after clicking a graph node: its risk assessment, connections, and evidence already found

## Open Source Contribution

The GitHub miner (`backend/agents/git_miner.py`) is designed to be
packaged and contributed upstream as a standalone DataHub ingestion skill —
it only depends on `PyGithub` and returns plain `EvidenceSource` records,
so it can run independently of the rest of the Lore pipeline.

## License

Apache 2.0 — see [LICENSE](LICENSE).
