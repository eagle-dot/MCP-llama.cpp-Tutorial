# MCP-llama.cpp-demo

Build a **fully local AI agent** using:

-   🦙 **llama.cpp**
-   🤖 **Qwen2.5-1.5B-Instruct (GGUF)**
-   🔌 **Model Context Protocol (MCP)**
-   🐍 **Python**

> **No OpenAI API key. No cloud inference. Everything runs locally.**

------------------------------------------------------------------------

## Overview

This repository demonstrates how to build an AI application where a
locally hosted LLM can invoke external tools through the **Model Context
Protocol (MCP)**.

The model is served by **llama.cpp** using its OpenAI-compatible REST
API, while Python orchestrates communication between the LLM and MCP
tools.

------------------------------------------------------------------------

## What You'll Learn

This project demonstrates how to:

-   Run an LLM locally using **llama.cpp**
-   Host a GGUF model with **llama-server.exe**
-   Access the model through the **OpenAI-compatible REST API**
-   Build an **MCP server** that exposes tools
-   Build an **MCP host** that allows the LLM to invoke those tools
-   Understand the complete MCP tool-calling workflow

------------------------------------------------------------------------

## Architecture

``` text
                +-----------------------+
                |   User Application    |
                +-----------+-----------+
                            |
                            v
                  llama_mcp_host.py
                            |
          +-----------------+-----------------+
          |                                   |
          v                                   v
  llama-server.exe                     MCP Server
(Qwen2.5-1.5B-Instruct)        (calculator_server.py)
          |                                   |
          |                           Calculator Tools
          |
 OpenAI-Compatible REST API
```

------------------------------------------------------------------------

## Repository Structure

``` text
mcp-llama.cpp-demo/
│
├── calculator_server.py      # MCP server exposing calculator tools
├── client.py                 # Basic MCP client (no LLM)
├── llama_mcp_host.py         # LLM + MCP orchestration
├── requirements.txt
└── README.md
```

------------------------------------------------------------------------

## Software Requirements

-   Windows 10 / 11
-   Python 3.11+
-   Conda (recommended)
-   NVIDIA GPU (optional but recommended)
-   CUDA-enabled **llama.cpp** build

------------------------------------------------------------------------

## Technology Stack

  Component               Purpose
  ----------------------- --------------------------------
  llama.cpp               Local LLM inference
  Qwen2.5-1.5B-Instruct   Language model
  llama-server            OpenAI-compatible model server
  MCP                     Tool communication protocol
  Python                  Application and orchestration

------------------------------------------------------------------------

## References

-   **Model Context Protocol (MCP)**\
    https://modelcontextprotocol.io

-   **MCP Python SDK**\
    https://github.com/modelcontextprotocol/python-sdk

-   **llama.cpp**\
    https://github.com/ggml-org/llama.cpp

-   **Qwen Models (Hugging Face)**\
    https://huggingface.co/Qwen

------------------------------------------------------------------------

## License

This project is provided for educational and demonstration purposes.
