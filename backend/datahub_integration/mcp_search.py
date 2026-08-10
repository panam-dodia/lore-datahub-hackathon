"""Runs DataHub MCP Server searches via a fully isolated subprocess.

mcp-server-datahub's dependencies hard-conflict with this app's FastAPI
version (confirmed by hand: even the bare `mcp` client SDK pulls in a
starlette version FastAPI 0.111.0 rejects), so it can never be imported
into this process. Instead, mcp_bridge/ is its own venv with its own
dependencies, and this just shells out to it.

Uses the synchronous `subprocess` module (via asyncio.to_thread) rather
than asyncio.create_subprocess_exec — the latter requires the Proactor
event loop, but uvicorn runs the Selector loop on Windows by default,
where async subprocess spawning raises NotImplementedError outright.
"""

import asyncio
import json
import os
import subprocess

_BRIDGE_DIR = os.path.join(os.path.dirname(__file__), "..", "mcp_bridge")
_BRIDGE_PYTHON = os.path.join(_BRIDGE_DIR, ".venv", "Scripts", "python.exe")
_BRIDGE_SCRIPT = os.path.join(_BRIDGE_DIR, "search.py")


def _run_bridge(query: str) -> list[dict]:
    result = subprocess.run(
        [_BRIDGE_PYTHON, _BRIDGE_SCRIPT, query],
        capture_output=True,
        text=True,
        env=os.environ.copy(),
    )
    if result.returncode != 0:
        raise RuntimeError(f"MCP search bridge failed: {result.stderr}")
    return json.loads(result.stdout)


async def search_via_mcp(query: str) -> list[dict]:
    return await asyncio.to_thread(_run_bridge, query)
