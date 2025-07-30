import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def run_tool_tests(server_script: str):
    print("Connecting to MCP server via stdio...\n")

    server_params = StdioServerParameters(
        command="python",
        # args=[server_script],
        args=["-m", "mcp_abc_mock.server_stdio"],
    )

    async with stdio_client(server_params) as (reader, writer):
        async with ClientSession(reader, writer) as session:
            # await session.initialize()

            # # --- get_project_names ---
            # print(">>> Testing: get_project_names()")
            # response = await session.call_tool("get_project_names", {})
            # for item in response.content:
            #     print(item.text)
            # print()

            # --- get_full_abc_data ---
            print(">>> Testing: get_full_abc_data()")
            response = await session.call_tool("get_full_abc_data", {})
            print(f"[INFO] Returned {len(response.content)} rows")
            for i, item in enumerate(response.content, 1):  # first 5 only
                parsed = json.loads(item.text)
                print(f"\n--- Entry {i} ---")
                print(json.dumps(parsed, indent=2))
            print()

            # # --- get_abc_data_filtered ---
            # print(">>> Testing: get_abc_data_filtered('NMR')")
            # response = await session.call_tool(
            #     "get_abc_data_filtered", {"project_name": "NMR"}
            # )
            # print(f"[INFO] Returned {len(response.content)} rows")
            # for i, item in enumerate(response.content, 1):  # first 5 only
            #     parsed = json.loads(item.text)
            #     print(f"\n--- Entry {i} ---")
            #     print(json.dumps(parsed, indent=2))
            # print()

            # # --- abc_data_description ---
            # print(">>> Testing: abc_data_description()")
            # response = await session.call_tool("abc_data_description", {})
            # for item in response.content:
            #     parsed = json.loads(item.text)
            #     print(json.dumps(parsed, indent=2))
            # print()


if __name__ == "__main__":
    import os

    script_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "server_stdio.py")
    )

    asyncio.run(run_tool_tests(script_path))
