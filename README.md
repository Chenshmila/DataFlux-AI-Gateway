# DataFlux AI Gateway

An AI-powered gateway for discovering and analyzing Data Products using the Model Context Protocol (MCP). The system uses Claude as the reasoning layer to match customers with the right curated dataset for their ML, BI, or analytical workload.

---

## Project Overview

| Component | File | Role |
|---|---|---|
| MCP Server | `agent_store.py` | Encapsulates the data product catalog and exposes self-describing tools |
| Agent Client | `agent.py` | Orchestrates the conversation and manages the LLM agentic loop |
| Shared Config | `config.py` | Single source of truth for the shared secret and other constants |
| Authentication | `os.environ` | Secure access via `DATAFLUX_INTERNAL_KEY` |

---

## Why MCP instead of REST?

- **Self-Describing Tools** - In traditional REST APIs, you need separate documentation (like Swagger) to explain endpoints. In MCP, the agent runs `list_tools()` at runtime and discovers exactly what the server can do, what data it needs, and how to use it - all in real-time.
- **Built-in Data Validation (JSON Schema)** - MCP acts as a "gatekeeper." Every tool has a defined schema, ensuring that if the LLM tries to send incorrect data types, the protocol stops it before it ever hits the business logic. This makes the system significantly more robust.
- **Swappable Transport (Scalability)** - Currently the system uses `stdio` for local development. MCP allows switching to `HTTP/SSE` with a single line of code, enabling the system to scale from a single user to millions without rewriting the core logic.
- **Modular Composition** - MCP allows connecting multiple servers (e.g., one for data products, one for billing, one for data quality reports) to a single agent. The agent sees them all under one namespace, enabling extreme modularity without complex integration code.

---

## Bonus Requirements Implemented

- **Second Agent & Use Case** - Two distinct personas: **Dara** (Data Strategy Consultant) for product consultation, and **Quinn** (Data FinOps Specialist) for cost analysis and budget-to-dataset matching.
- **Gateway Authentication** - A security layer requiring a shared secret (`DATAFLUX_INTERNAL_KEY`) to authorize communication between the gateway and the MCP server. Both sides validate the key against a single `EXPECTED_KEY` constant defined in `config.py`, ensuring a **Single Source of Truth** for the secret while keeping the client and server **loosely coupled** - neither file imports the other; they both depend only on the shared config module. In production, `config.py` would delegate to a Secret Manager rather than holding a hardcoded value.
- **Dynamic Discoverability** - Leveraging MCP's `list_tools()`, the gateway discovers available tools at runtime. This allows new agents to "know" capabilities instantly without code changes.
- **Edge Case Handling** - `search_products` is designed to return actionable guidance when no data assets match, preventing agent hallucinations and guiding the user effectively.
- **Multiple Interface Options** - Supports both interactive CLI mode (for low-latency testing) and `DEBUG=true` JSON logging (to inspect protocol-level MCP traffic).

---

## Future Improvements (Production Roadmap)

- **Persistent Conversation Memory** - Transitioning from in-memory history to a persistent store (e.g., Redis) for long-term context retention across sessions.
- **Structured JSON Logging** - Moving to structured logging for integration with observability platforms, enabling automated monitoring of agent interactions.
- **Automated Testing** - Implementing unit and integration tests using Pytest to test the agentic loop without incurring API costs.
- **Rate Limiting & Audit Trail** - Implementing request throttling and detailed access logs - critical for a multi-tenant data marketplace platform.

---

## Setup & Usage

**Requirements:** Python 3.10+

```bash
# 1. Setup
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# 2. Set keys & run
export ANTHROPIC_API_KEY="sk-ant-..."
export DATAFLUX_INTERNAL_KEY="dataflux-master-secret-2026"

python agent.py --mode sales    # Dara (Data Strategy Consultant)
python agent.py --mode pricing  # Quinn (Data FinOps Specialist)
```
