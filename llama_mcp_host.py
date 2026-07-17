import asyncio
import json
import sys
from pathlib import Path
from typing import Any

import httpx
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


LLAMA_URL = "http://127.0.0.1:8081/v1/chat/completions"
MODEL_NAME = "local-model"

PROJECT_DIR = Path(__file__).resolve().parent
MCP_SERVER_FILE = PROJECT_DIR / "calculator_server.py"


def mcp_tools_to_openai(mcp_tools: list[Any]) -> list[dict[str, Any]]:
    """
    Convert MCP tool descriptions into the OpenAI-compatible tool format
    expected by llama-server.
    """
    converted_tools = []

    for tool in mcp_tools:
        converted_tools.append(
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description or "",
                    "parameters": tool.inputSchema,
                },
            }
        )

    return converted_tools


def extract_mcp_result_text(result: Any) -> str:
    """
    Convert an MCP CallToolResult into text that can be returned to the LLM.
    """
    output_parts = []

    for item in result.content:
        if hasattr(item, "text"):
            output_parts.append(item.text)
        else:
            output_parts.append(str(item))

    return "\n".join(output_parts)


async def call_llama(
    messages: list[dict[str, Any]],
    tools: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """
    Send a chat-completion request to llama-server.
    """
    payload: dict[str, Any] = {
        "model": MODEL_NAME,
        "messages": messages,
        "temperature": 0,
    }

    if tools:
        payload["tools"] = tools
        payload["tool_choice"] = "auto"

    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(LLAMA_URL, json=payload)
        response.raise_for_status()
        data = response.json()

    return data["choices"][0]["message"]


async def run_agent(user_question: str) -> None:
    if not MCP_SERVER_FILE.exists():
        raise FileNotFoundError(
            f"MCP server file not found: {MCP_SERVER_FILE}"
        )

    # This describes how the MCP client should start the MCP server.
    server_parameters = StdioServerParameters(
        command=sys.executable,
        args=[str(MCP_SERVER_FILE)],
        env=None,
    )

    # Start the MCP server and connect to it over stdin/stdout.
    async with stdio_client(server_parameters) as (
        read_stream,
        write_stream,
    ):
        async with ClientSession(read_stream, write_stream) as session:
            # Required MCP initialization handshake.
            await session.initialize()

            # Ask the MCP server which tools it provides.
            tool_list_result = await session.list_tools()
            mcp_tools = tool_list_result.tools

            print("\nTools discovered from MCP server:")

            for tool in mcp_tools:
                print(f"  - {tool.name}: {tool.description}")

            # Convert MCP schemas into the format understood by llama.cpp.
            openai_tools = mcp_tools_to_openai(mcp_tools)

            messages: list[dict[str, Any]] = [
                {
                    "role": "system",
                    "content": (
                        "You are a helpful assistant. "
                        "Use the supplied tools whenever they are appropriate. "
                        "Do not calculate arithmetic yourself when a calculator "
                        "tool is available."
                    ),
                },
                {
                    "role": "user",
                    "content": user_question,
                },
            ]

            # First request: let the LLM decide whether to call an MCP tool.
            assistant_message = await call_llama(
                messages=messages,
                tools=openai_tools,
            )

            messages.append(assistant_message)

            tool_calls = assistant_message.get("tool_calls", [])

            if not tool_calls:
                print("\nThe model did not request an MCP tool.")
                print("\nLLM response:")
                print(assistant_message.get("content", ""))
                return

            # Execute every tool requested by the model.
            for tool_call in tool_calls:
                function_data = tool_call["function"]
                tool_name = function_data["name"]

                raw_arguments = function_data.get("arguments", "{}")

                if isinstance(raw_arguments, str):
                    tool_arguments = json.loads(raw_arguments)
                else:
                    tool_arguments = raw_arguments

                print(f"\nLLM requested MCP tool: {tool_name}")
                print(
                    "Arguments:",
                    json.dumps(tool_arguments, indent=2),
                )

                # This is the actual MCP invocation.
                result = await session.call_tool(
                    tool_name,
                    arguments=tool_arguments,
                )

                result_text = extract_mcp_result_text(result)

                print("MCP server returned:", result_text)

                # Send the MCP result back to the LLM.
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "content": result_text,
                    }
                )

            # Second request: ask the LLM to turn the tool result into an answer.
            final_message = await call_llama(
                messages=messages,
                tools=openai_tools,
            )

            print("\nFinal LLM response:")
            print(final_message.get("content", ""))


async def main() -> None:
    question = input("Ask a question: ").strip()

    if not question:
        print("Please enter a question.")
        return

    try:
        await run_agent(question)
    except httpx.ConnectError:
        print(
            "\nCould not connect to llama-server at "
            "http://127.0.0.1:8081."
        )
        print("Make sure llama-server.exe is running.")
    except httpx.HTTPStatusError as exc:
        print("\nllama-server returned an HTTP error:")
        print(exc.response.text)
    except json.JSONDecodeError as exc:
        print(f"\nThe model returned invalid tool arguments: {exc}")
    except Exception as exc:
        print(f"\nError: {type(exc).__name__}: {exc}")


if __name__ == "__main__":
    asyncio.run(main())