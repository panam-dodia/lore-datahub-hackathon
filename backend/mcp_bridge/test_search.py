import asyncio
import json
import os

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER_EXE = os.path.join(os.path.dirname(__file__), ".venv", "Scripts", "mcp-server-datahub.exe")


async def main():
    server_params = StdioServerParameters(
        command=SERVER_EXE,
        args=[],
        env={"DATAHUB_GMS_URL": "http://localhost:8080", "DATAHUB_GMS_TOKEN": ""},
    )
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(
                "search",
                {"query": "/q order", "filter": "entity_type = dataset", "num_results": 3},
            )
            for content in result.content:
                if hasattr(content, "text"):
                    parsed = json.loads(content.text)
                    print(json.dumps(parsed, indent=2)[:3000])
                else:
                    print(content)


asyncio.run(main())
