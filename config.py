"""
DataFlux Solutions centralized configuration.

This module is the single source of truth for shared constants used by both
the MCP server (agent_store.py) and the agent client (agent.py).

In production, EXPECTED_KEY should NOT be hardcoded here. Instead, load it
at startup from a secure Secret Manager (e.g. HashiCorp Vault, AWS Secrets
Manager, GCP Secret Manager) so that the secret is never stored in source
control.
"""

# Shared secret that must match the value exported as DATAFLUX_INTERNAL_KEY
# in the environment before running agent.py or agent_store.py.
EXPECTED_KEY = "dataflux-master-secret-2026"
