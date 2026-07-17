import asyncio
import json
import sys
from pathlib import Path
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


PROJECT_DIR = Path(r"I:\technology\mcp-llama-demo")
SERVER_FILE = PROJECT_DIR / "calculator_server.py"


def content_to_text(content: list[Any]) -> str:
    """
    Convert MCP content blocks into readable text.
    """

    output: list[str] = []

    for item in content:
        if hasattr(item, "text"):
            output.append(str(item.text))
        else:
            output.append(str(item))

    return "\n".join(output)


async def run_client() -> None:
    """
    Start calculator_server.py as a subprocess, connect through MCP stdio,
    list its tools, and call the multiply and add tools.
    """

    if not SERVER_FILE.exists():
        raise FileNotFoundError(
            f"MCP server was not found:\n{SERVER_FILE}"
        )

    print("MCP server:")
    print(SERVER_FILE)

    print("\nPython interpreter:")
    print(sys.executable)

    # Tell the MCP client how to start calculator_server.py.
    #
    # sys.executable points to the Python executable in your active
    # Conda environment.
    server_parameters = StdioServerParameters(
        command=sys.executable,
        args=[str(SERVER_FILE)],
        env=None,
    )

    print("\nStarting MCP server...")

    # stdio_client starts calculator_server.py as a child process.
    # Communication occurs through stdin and stdout.
    async with stdio_client(server_parameters) as (
        read_stream,
        write_stream,
    ):
        async with ClientSession(
            read_stream,
            write_stream,
        ) as session:

            # Perform the MCP initialization handshake.
            await session.initialize()

            print("Connected to MCP server.")

            # Ask the server which tools are available.
            tools_result = await session.list_tools()

            print("\nAvailable MCP tools:")

            for tool in tools_result.tools:
                print(f"\nTool name: {tool.name}")
                print(f"Description: {tool.description}")

                input_schema = getattr(tool, "inputSchema", None)

                if input_schema is not None:
                    print("Input schema:")
                    print(json.dumps(input_schema, indent=2))

            # Call the multiply tool directly.
            print("\nCalling multiply(a=25, b=17)...")

            multiply_result = await session.call_tool(
                "multiply",
                arguments={
                    "a": 25,
                    "b": 17,
                },
            )

            print("Raw multiply result:")
            print(multiply_result)

            print("\nReadable multiply result:")
            print(content_to_text(multiply_result.content))

            # Call the add tool directly.
            print("\nCalling add(a=100, b=23)...")

            add_result = await session.call_tool(
                "add",
                arguments={
                    "a": 100,
                    "b": 23,
                },
            )

            print("Raw add result:")
            print(add_result)

            print("\nReadable add result:")
            print(content_to_text(add_result.content))

            # Check whether the MCP server reported an error.
            if multiply_result.isError:
                print("\nThe multiply tool reported an error.")

            if add_result.isError:
                print("\nThe add tool reported an error.")


async def main() -> None:
    try:
        await run_client()

    except FileNotFoundError as exc:
        print(f"\nFile error:\n{exc}")

    except ModuleNotFoundError as exc:
        print(f"\nMissing Python package:\n{exc}")
        print('\nInstall it with: pip install "mcp[cli]"')

    except KeyboardInterrupt:
        print("\nStopped by user.")

    except Exception as exc:
        print(
            f"\nUnexpected error: "
            f"{type(exc).__name__}: {exc}"
        )


if __name__ == "__main__":
    asyncio.run(main())