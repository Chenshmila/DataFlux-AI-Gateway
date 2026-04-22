"""
mock_demo.py - Simulated agent conversation (no API key required)

Demonstrates exactly what happens at runtime:
  1. Agent connects to the MCP server and discovers tools
  2. User asks a question
  3. Agent decides which tool to call and with what arguments
  4. MCP server returns structured data
  5. Agent composes a recommendation from the tool result

Run with:
    python mock_demo.py
"""

import json
import time

# Import the real tool functions - the MCP server logic runs for real.
from agent_store import get_catalog, search_products


# ---------------------------------------------------------------------------
# Minimal terminal formatting helpers
# ---------------------------------------------------------------------------

RESET  = "\033[0m"
BOLD   = "\033[1m"
CYAN   = "\033[96m"
YELLOW = "\033[93m"
GREEN  = "\033[92m"
GREY   = "\033[90m"
BLUE   = "\033[94m"


def header(text: str) -> None:
    print(f"\n{BOLD}{CYAN}{'─' * 60}{RESET}")
    print(f"{BOLD}{CYAN}  {text}{RESET}")
    print(f"{BOLD}{CYAN}{'─' * 60}{RESET}\n")


def speaker(name: str, text: str, color: str = RESET) -> None:
    print(f"{BOLD}{color}{name}:{RESET} {text}\n")
    time.sleep(0.4)


def tool_call(name: str, args: dict) -> None:
    args_str = json.dumps(args, ensure_ascii=False)
    print(f"  {YELLOW}▶ tool call  {BOLD}{name}{RESET}{YELLOW}({args_str}){RESET}")
    time.sleep(0.3)


def tool_result(data: dict) -> None:
    pretty = json.dumps(data, indent=4, ensure_ascii=False)
    indented = "\n".join("    " + line for line in pretty.splitlines())
    print(f"  {GREY}◀ tool result{RESET}")
    print(f"{GREY}{indented}{RESET}\n")
    time.sleep(0.4)


def separator() -> None:
    print(f"{GREY}{'· ' * 30}{RESET}\n")
    time.sleep(0.2)


# ---------------------------------------------------------------------------
# Simulated agent response builder
# ---------------------------------------------------------------------------

def build_recommendation(product: dict) -> str:
    features = "\n".join(f"    • {f}" for f in product["features"])
    return (
        f"Based on your needs, I recommend **{product['name']}** "
        f"at {product['price']}.\n\n"
        f"  Delivered via {', '.join(product['platforms'])} and includes:\n"
        f"{features}\n\n"
        f"  {product['best_for']}\n\n"
        f"  Ready to get started? You can subscribe directly - no sales call needed."
    )


# ---------------------------------------------------------------------------
# Demo turns
# ---------------------------------------------------------------------------

TURNS = [
    {
        "label": "Turn 1 - Broad opening question",
        "user": "Hi! What data products do you offer?",
        "think": 'User wants an overview → call get_catalog() to fetch all products.',
        "calls": [
            {"tool": "get_catalog", "args": {}, "fn": get_catalog},
        ],
        "response": (
            "Hi! I'm Dara from DataFlux Solutions. We offer three curated data products "
            "designed for different stages of your data journey:\n\n"
            "  • MarketTrends Basic      - $100/month  (real-time retail signals, CSV/JSON)\n"
            "  • ConsumerInsights Pro     -$500/month  (consumer behavior, Parquet/Snowflake/S3)\n"
            "  • GlobalAnalytics Enterprise - custom pricing (macroeconomic datasets, full SLA)\n\n"
            "What are you building - an ML model, a BI dashboard, or a data warehouse?"
        ),
    },
    {
        "label": "Turn 2 - Specific need expressed",
        "user": (
            "I'm training a churn prediction model in Python. "
            "My pipeline runs on Snowflake and I need anonymized consumer behavior data "
            "with feature labels ready for ML. Which product fits?"
        ),
        "think": (
            'Customer mentioned "churn prediction", "Snowflake", and "ML feature labels". '
            'Call search_products() with those keywords to find the best match.'
        ),
        "calls": [
            {
                "tool": "search_products",
                "args": {"query": "churn prediction Snowflake ML feature labels"},
                "fn": lambda: search_products("churn prediction Snowflake ML feature labels"),
            },
        ],
        "response_fn": lambda result: build_recommendation(
            next(p for p in result["matches"] if p["id"] == "consumerinsights_pro")
        ),
    },
    {
        "label": "Turn 3 - Edge case: non-existent product",
        "user": "Do you have a 'DataFlux Ultra' plan?",
        "think": (
            '"DataFlux Ultra" is not in the catalog. '
            'Call search_products() to confirm no match, then clarify.'
        ),
        "calls": [
            {
                "tool": "search_products",
                "args": {"query": "DataFlux Ultra"},
                "fn": lambda: search_products("DataFlux Ultra"),
            },
        ],
        "response": (
            "We don't have a 'DataFlux Ultra' plan - our top tier is "
            "**GlobalAnalytics Enterprise**, which includes global macroeconomic datasets, "
            "alternative data feeds, custom delivery schemas, a dedicated data engineer, "
            "and a contractual SLA.\n\n"
            "If you need custom enterprise pricing, I can connect you with our "
            "team at sales@dataflux-ai.io. Would that be helpful?"
        ),
    },
]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    header("DataFlux AI Gateway - Mock Demo")
    print(
        f"  {GREY}This script runs the real MCP tool functions (agent_store.py)\n"
        f"  and simulates the Claude agent reasoning layer.\n"
        f"  No API key is required.{RESET}\n"
    )

    for turn in TURNS:
        header(turn["label"])

        # User message
        speaker("You ", turn["user"], BLUE)

        # Internal reasoning
        print(f"  {GREY}[agent reasoning] {turn['think']}{RESET}\n")
        time.sleep(0.3)

        # Tool calls - real functions, real results
        last_result = None
        for call in turn["calls"]:
            tool_call(call["tool"], call["args"])
            last_result = call["fn"]()
            tool_result(last_result)

        # Agent response
        if "response_fn" in turn:
            response_text = turn["response_fn"](last_result)
        else:
            response_text = turn["response"]

        speaker("Dara", response_text, GREEN)
        separator()

    print(f"{BOLD}Demo complete.{RESET}  To run the live agent: "
          f"{CYAN}export ANTHROPIC_API_KEY=sk-ant-... && python agent.py{RESET}\n")


if __name__ == "__main__":
    main()
