"""Standalone bridge script — runs inside mcp_bridge/.venv, a Python
environment fully isolated from the main backend's. mcp-server-datahub's
dependencies (sse-starlette>=0.49.1) hard-conflict with our FastAPI
version's (starlette<0.38.0), so this can never share a process with the
main app; it's invoked as a subprocess instead (see
datahub_integration/mcp_search.py).

Usage: python search.py "<query>"  -> prints a JSON array of {urn, name} to stdout.
"""

import asyncio
import json
import os
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER_EXE = os.path.join(os.path.dirname(__file__), ".venv", "Scripts", "mcp-server-datahub.exe")


async def search(query: str, num_results: int = 10) -> list[dict]:
    server_params = StdioServerParameters(
        command=SERVER_EXE,
        args=[],
        env={
            "DATAHUB_GMS_URL": os.environ.get("DATAHUB_GMS_URL", "http://localhost:8080"),
            "DATAHUB_GMS_TOKEN": os.environ.get("DATAHUB_TOKEN", ""),
        },
    )
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # The server's recommended syntax for matching multiple words is
            # "+"-joined terms (AND) behind a "/q" prefix; an empty query
            # falls back to a wildcard match instead.
            terms = query.strip().split()
            mcp_query = f"/q {'+'.join(terms)}" if terms else "*"

            result = await session.call_tool(
                "search",
                {"query": mcp_query, "filter": "entity_type = dataset", "num_results": num_results},
            )
            for content in result.content:
                if hasattr(content, "text"):
                    parsed = json.loads(content.text)
                    return [
                        {
                            "urn": r["entity"]["urn"],
                            "name": r["entity"].get("properties", {}).get("name", r["entity"]["urn"]),
                        }
                        for r in parsed.get("searchResults", [])
                    ]
            return []


if __name__ == "__main__":
    query_arg = sys.argv[1] if len(sys.argv) > 1 else ""
    print(json.dumps(asyncio.run(search(query_arg))))
