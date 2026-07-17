# MCP-llama.cpp-demo
Build a fully local AI agent using:   
  llama.cpp  Qwen2.5-1.5B-Instruct (GGUF) 
  Model Context Protocol (MCP) 
  Python  
No OpenAI API key. No cloud inference. Everything runs locally.


What You'll Learn

This project demonstrates how to:

Run an LLM locally using llama.cpp

Host the model using llama-server.exe

Call the model through the OpenAI-compatible REST API

Build an MCP server that exposes tools

Build an MCP host that lets the LLM invoke those tools

Understand the complete tool-calling workflow

Repository Structure

mcp-llama-demo/
│
├── calculator_server.py      # MCP server exposing calculator tools
├── client.py                 # Basic MCP client (no LLM)
├── llama_mcp_host.py         # LLM + MCP orchestration
├── requirements.txt
└── README.md

Software Requirements

Windows 10/11

Python 3.11+

Conda (recommended)

NVIDIA GPU (optional but recommended)

CUDA-enabled llama.cpp build




References

Model Context Protocol: https://modelcontextprotocol.io

MCP Python SDK: https://github.com/modelcontextprotocol/python-sdk

llama.cpp: https://github.com/ggml-org/llama.cpp

Hugging Face Qwen Models: https://huggingface.co/Qwen
