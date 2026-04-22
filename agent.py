"""
DataFlux Solutions Customer Agent
==================================
An interactive CLI agent that connects to the DataFlux Solutions MCP server
(agent_store.py) over stdio and uses Claude to answer customer queries.

Usage:
    python agent.py [--mode sales|pricing]

Requirements:
    ANTHROPIC_API_KEY must be set in the environment.

How it works:
    1. Spawns agent_store.py as a subprocess (stdio MCP transport).
    2. Discovers available tools via the MCP protocol.
    3. Converts MCP tool schemas to the Anthropic tool-use format.
    4. Runs an agentic loop: Claude reasons, calls tools, gets results,
       and produces a final answer — all within a single user turn.
"""

import argparse
import asyncio
import json
import logging
import os
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Silence MCP internal logs (INFO-level noise like "Processing request...")
# Promote to DEBUG=true to restore full output.
# ---------------------------------------------------------------------------

DEBUG = os.environ.get("DEBUG", "").lower() == "true"

logging.getLogger("mcp").setLevel(logging.DEBUG if DEBUG else logging.WARNING)


def _debug(*args, **kwargs) -> None:
    if DEBUG:
        print(*args, **kwargs)

import anthropic
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from config import EXPECTED_KEY

# ---------------------------------------------------------------------------
# Persona configuration
# ---------------------------------------------------------------------------

PERSONAS = {
    "sales": {
        "name": "Dara",
        "prompt_file": "system_prompt.md",
    },
    "pricing": {
        "name": "Quinn",
        "prompt_file": "pricing_prompt.md",
    },
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _mcp_tool_to_anthropic(tool) -> dict:
    """Convert an MCP tool definition to the Anthropic tool-use schema."""
    return {
        "name": tool.name,
        "description": tool.description or "",
        "input_schema": tool.inputSchema,
    }


async def _call_mcp_tool(session: ClientSession, name: str, arguments: dict) -> str:
    """Call an MCP tool and return the result as a plain string."""
    result = await session.call_tool(name, arguments=arguments)
    # MCP returns a list of content blocks; we join text blocks.
    parts = []
    for block in result.content:
        if hasattr(block, "text"):
            parts.append(block.text)
        else:
            parts.append(str(block))
    return "\n".join(parts) if parts else "(empty result)"


# ---------------------------------------------------------------------------
# Agentic loop
# ---------------------------------------------------------------------------


async def run_agent(messages: list, session: ClientSession, client: anthropic.Anthropic, system_prompt: str) -> str:
    """
    Run one turn of the agentic loop against a persistent messages list.

    The caller appends the new user message before invoking this function.
    Tool calls and their results are appended in-place so subsequent turns
    retain full context.  The loop continues until Claude stops requesting
    tool calls and returns the final text.
    """
    # Discover tools from the MCP server
    mcp_tools = (await session.list_tools()).tools
    anthropic_tools = [_mcp_tool_to_anthropic(t) for t in mcp_tools]

    while True:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system=system_prompt,
            tools=anthropic_tools,
            messages=messages,
        )

        # Append Claude's response to the conversation history
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "end_turn":
            # Extract the final text response
            for block in response.content:
                if hasattr(block, "text"):
                    return block.text
            return "(no text response)"

        if response.stop_reason != "tool_use":
            return f"(unexpected stop reason: {response.stop_reason})"

        # Process all tool calls in this turn
        tool_results = []
        for block in response.content:
            if block.type != "tool_use":
                continue

            _debug(f"  [tool call] {block.name}({json.dumps(block.input, ensure_ascii=False)})")
            result_text = await _call_mcp_tool(session, block.name, block.input)
            _debug(f"  [tool result] {result_text[:120]}{'...' if len(result_text) > 120 else ''}")

            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": result_text,
            })

        messages.append({"role": "user", "content": tool_results})


# ---------------------------------------------------------------------------
# Interactive CLI
# ---------------------------------------------------------------------------


async def main() -> None:
    parser = argparse.ArgumentParser(description="DataFlux Solutions Customer Agent")
    parser.add_argument(
        "--mode",
        choices=list(PERSONAS.keys()),
        default="sales",
        help="Agent persona to use (default: sales)",
    )
    args = parser.parse_args()

    persona = PERSONAS[args.mode]
    agent_name = persona["name"]
    prompt_path = Path(__file__).parent / persona["prompt_file"]
    system_prompt = prompt_path.read_text(encoding="utf-8")

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("Error: ANTHROPIC_API_KEY is not set.", file=sys.stderr)
        sys.exit(1)

    internal_key = os.environ.get("DATAFLUX_INTERNAL_KEY", "")
    if not internal_key:
        print("Error: DATAFLUX_INTERNAL_KEY is not set.", file=sys.stderr)
        sys.exit(1)
    if internal_key != EXPECTED_KEY:
        print(
            "Error: DATAFLUX_INTERNAL_KEY does not match the expected secret. "
            "The agent cannot authenticate with the MCP server.",
            file=sys.stderr,
        )
        sys.exit(1)

    server_params = StdioServerParameters(
        command=sys.executable,
        args=[str(Path(__file__).parent / "agent_store.py")],
        env={**os.environ, "DATAFLUX_INTERNAL_KEY": internal_key},
    )

    client = anthropic.Anthropic()

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = (await session.list_tools()).tools
            _debug(f"Connected to DataFlux Solutions MCP server. Tools available: {[t.name for t in tools]}")
            print(f"Welcome to DataFlux Solutions. You are speaking with {agent_name}. Type your question (or 'quit' to exit).\n")

            # Persistent conversation history — grows across turns so Claude
            # retains context for follow-up questions.
            messages: list = []

            while True:
                try:
                    user_input = input("You: ").strip()
                except (EOFError, KeyboardInterrupt):
                    print("\nGoodbye!")
                    break

                if not user_input:
                    continue
                if user_input.lower() in {"quit", "exit", "q"}:
                    print("Goodbye!")
                    break

                # Append the new user turn before handing off to the agent loop.
                messages.append({"role": "user", "content": user_input})

                print()
                answer = await run_agent(messages, session, client, system_prompt)
                print(f"{agent_name}: {answer}\n")


if __name__ == "__main__":
    asyncio.run(main())
