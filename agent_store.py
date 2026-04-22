"""
DataFlux Solutions MCP Server - the agent-facing data product catalog gateway.

Exposes two tools:
  - get_catalog     : return every data product with full details
  - search_products : filter data products by free-text query

Authentication:
    DATAFLUX_INTERNAL_KEY must be set in the environment and must match
    the expected shared secret. Both tools reject calls when the key is
    absent or incorrect.

Run standalone for development:
    DATAFLUX_INTERNAL_KEY=dataflux-master-secret-2026 python agent_store.py
"""

import logging
import os

# Silence MCP internal INFO logs (e.g. "Processing request of type ...")
logging.getLogger("mcp").setLevel(logging.WARNING)

from mcp.server.fastmcp import FastMCP
from config import EXPECTED_KEY

# ---------------------------------------------------------------------------
# Shared-secret authentication
# ---------------------------------------------------------------------------

_INTERNAL_KEY = os.environ.get("DATAFLUX_INTERNAL_KEY", "")


def _check_auth() -> str | None:
    """Return an error string if the internal key is missing or incorrect, else None."""
    if not _INTERNAL_KEY:
        return (
            "Unauthorized: DATAFLUX_INTERNAL_KEY is not set. "
            "The agent must export this variable before starting the server."
        )
    if _INTERNAL_KEY != EXPECTED_KEY:
        return (
            "Unauthorized: DATAFLUX_INTERNAL_KEY does not match the expected secret. "
            "Ensure the correct shared key is exported in the environment."
        )
    return None

mcp = FastMCP(
    name="DataFlux Solutions Data Catalog",
    instructions=(
        "You are a tool server that provides accurate DataFlux Solutions data product "
        "information. Always return structured data so the calling agent can "
        "present it clearly to end-users."
    ),
)

# ---------------------------------------------------------------------------
# Catalog data - single source of truth
# ---------------------------------------------------------------------------

CATALOG: dict[str, dict] = {
    "markettrends_basic": {
        "id": "markettrends_basic",
        "name": "MarketTrends Basic",
        "price": "$100/month",
        "tier": "light",
        "platforms": ["CSV", "JSON API"],
        "features": [
            "Real-time retail pricing signals updated every 15 minutes",
            "Coverage across 50+ retail categories and 10,000+ SKUs",
            "JSON API for direct integration with BI dashboards",
            "CSV export for offline analysis and Excel/Power BI workflows",
        ],
        "best_for": "Small teams and analysts building BI dashboards who need affordable, real-time retail pricing intelligence.",
    },
    "consumerinsights_pro": {
        "id": "consumerinsights_pro",
        "name": "ConsumerInsights Pro",
        "price": "$500/month",
        "tier": "pro",
        "platforms": ["Parquet", "Snowflake", "S3"],
        "features": [
            "Granular, anonymized consumer behavior data - 50M+ monthly events",
            "Pre-built Parquet schema optimized for ML pipelines and feature stores",
            "Direct Snowflake data share - zero-copy, no ETL required",
            "S3 delivery with partitioned datasets ready for Spark and Pandas",
            "Churn prediction labels and purchase-intent signals included",
        ],
        "best_for": "ML engineers and data scientists training models for churn prediction, recommendation, or customer segmentation.",
    },
    "globalanalytics_enterprise": {
        "id": "globalanalytics_enterprise",
        "name": "GlobalAnalytics Enterprise",
        "price": "Contact us for pricing",
        "tier": "enterprise",
        "platforms": ["Parquet", "Snowflake", "S3", "BigQuery", "custom connectors"],
        "features": [
            "Full-scale global macroeconomic datasets - 190+ countries, 30+ years of history",
            "Alternative data feeds: satellite imagery signals, shipping indices, commodities",
            "Custom data schema and delivery cadence negotiated per contract",
            "Dedicated data engineer for onboarding and schema maintenance",
            "SLA-backed freshness guarantees and contractual data quality commitments",
            "Private data room option for regulatory compliance (GDPR, SOC 2)",
        ],
        "best_for": "Hedge funds, financial institutions, and large enterprises requiring global-scale datasets with contractual quality SLAs.",
    },
}


# ---------------------------------------------------------------------------
# MCP Tools
# ---------------------------------------------------------------------------


@mcp.tool()
def get_catalog() -> dict:
    """
    Return the complete DataFlux Solutions data product catalog.

    Use this tool when:
    - The user asks "what data products do you offer?", "show me all datasets", or similar.
    - You need an overview of all tiers before making a recommendation.

    Returns a dict keyed by product ID, each value containing:
      - name        : display name of the data asset
      - price       : pricing string (may be "Contact us" for Enterprise)
      - tier        : "light" | "pro" | "enterprise"
      - platforms   : list of supported delivery formats and data platforms
      - features    : list of human-readable data asset descriptions
      - best_for    : a short sentence describing the ideal customer

    Never fabricate product details - always call this tool first.
    """
    auth_error = _check_auth()
    if auth_error:
        return {"error": auth_error}
    return {"products": CATALOG, "total": len(CATALOG)}


@mcp.tool()
def search_products(query: str) -> dict:
    """
    Search the DataFlux Solutions data catalog using a free-text query.

    Use this tool when:
    - The user describes a need (e.g. "Snowflake", "ML training", "churn", "cheap").
    - The user names a specific product tier ("light", "pro", "enterprise").
    - The user asks for a recommendation and you want to narrow down data assets.

    How matching works (case-insensitive, multi-field):
    - Product name
    - Tier label
    - Delivery platform / format list
    - Feature and schema descriptions
    - best_for description
    - Price string (useful for queries like "contact" or "$100")

    Args:
        query: One or more keywords describing what the customer needs.
               Examples: "Snowflake Parquet", "churn prediction", "macroeconomic", "cheapest"

    Returns:
        {
          "query": <original query>,
          "matches": [ <product dicts for every match> ],
          "total_matches": <int>,
          "message": <human-readable summary or "no products found" guidance>
        }

    Edge cases:
    - Empty query → returns the full catalog (same as get_catalog).
    - No matches  → returns an empty matches list with a helpful message so the
                    agent can tell the user what IS available instead of failing silently.
    """
    auth_error = _check_auth()
    if auth_error:
        return {"error": auth_error}

    query = query.strip()

    if not query:
        return {
            "query": query,
            "matches": list(CATALOG.values()),
            "total_matches": len(CATALOG),
            "message": "No query provided - returning full catalog.",
        }

    tokens = query.lower().split()
    matches = []

    for product in CATALOG.values():
        searchable = " ".join([
            product["name"],
            product["tier"],
            product["price"],
            product["best_for"],
            " ".join(product["platforms"]),
            " ".join(product["features"]),
        ]).lower()

        if any(token in searchable for token in tokens):
            matches.append(product)

    if matches:
        message = f"Found {len(matches)} product(s) matching '{query}'."
    else:
        message = (
            f"No data products matched '{query}'. "
            "Consider broadening the search or calling get_catalog to show all options. "
            "Available tiers are: MarketTrends Basic ($100/mo, CSV/JSON API), "
            "ConsumerInsights Pro ($500/mo, Parquet/Snowflake/S3), and GlobalAnalytics Enterprise (contact us)."
        )

    return {
        "query": query,
        "matches": matches,
        "total_matches": len(matches),
        "message": message,
    }


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run(transport="stdio")
