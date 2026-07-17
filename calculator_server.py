import os
import sys
from datetime import datetime
from pathlib import Path

from mcp.server.fastmcp import FastMCP


LOG_FILE = Path(r"I:\technology\mcp-llama-demo\calculator.log")

def log(message: str) -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(
        f"[{timestamp}] [CALCULATOR SERVER PID={os.getpid()}] {message}",
        file=sys.stderr,
        flush=True,
    )
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] [CALCULATOR SERVER PID={os.getpid()}] {message}\n")


log("Python file loaded")

mcp = FastMCP("Calculator")


@mcp.tool()
def multiply(a: float, b: float) -> float:
    log(f"multiply invoked: a={a}, b={b}")

    result = a * b

    log(f"multiply returning: {result}")
    return result



@mcp.tool()
def add(a: float, b: float) -> float:
    log(f"add invoked: a={a}, b={b}")

    result = a + b

    log(f"add returning: {result}")
    return result


if __name__ == "__main__":
    log("Starting MCP stdio server")
    mcp.run(transport="stdio")