import asyncio
import os

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER_EXE = os.path.join(os.path.dirname(__file__), ".venv", "Scripts", "mcp-server-datahub.exe")


async def main():
    server_params = StdioServerParameters(
        command=SERVER_EXE,
        args=[],
        env={
            "DATAHUB_GMS_URL": "http://localhost:8080",
            "DATAHUB_GMS_TOKEN": "",
        },
    )
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            for tool in tools.tools:
                print(f"\n=== {tool.name} ===")
                print(tool.description)
                print("Input schema:", tool.inputSchema)


asyncio.run(main())
