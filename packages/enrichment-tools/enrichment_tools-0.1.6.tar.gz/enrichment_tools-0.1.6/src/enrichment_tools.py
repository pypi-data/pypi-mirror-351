"""
enrichment_tools.py

This script sets up a FastMCP server that exposes the Apollo.io enrichment API
as a tool, using an OpenAPI specification. It is designed to be run as a standalone
process, with API credentials provided via environment variables.

Key Features:
- Loads OpenAPI spec from a YAML file.
- Configures HTTP client with API key and/or access token from environment.
- Sets up route mapping for GET and POST requests as tool endpoints.
- Runs the FastMCP server using Server-Sent Events (SSE) transport.

Environment Variables:
- API_KEY: Apollo API key (optional, for authentication)
- ACCESS_TOKEN: Apollo access token (optional, for authentication)
"""

import os
import httpx
import yaml
from fastmcp import FastMCP
from fastmcp.server.openapi import RouteMap, RouteType

# --- Load OpenAPI Specification ---
# The OpenAPI spec defines the endpoints and schemas for the Apollo enrichment API.
# You can swap the path below for local development or testing.
with open("src/specs/enrichment.yaml", "r") as f:
    spec = yaml.safe_load(f)


# --- API Configuration ---
BASE_URL = 'https://api.apollo.io'


# Retrieve credentials from environment variables of the client
# These should be set by the MCP client or your shell environment.
API_KEY = os.environ.get("API_KEY")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")

# Prepare HTTP headers for authentication and request source tracking.
headers = {
    'request_source': 'mcp'  # Custom header to identify requests from MCP
}
if API_KEY:
    headers['x-api-key'] = API_KEY  # Apollo API key header
if ACCESS_TOKEN:
    headers["Authorization"] = ACCESS_TOKEN  # Apollo bearer token header

# --- HTTP Client Setup ---
# Use httpx.AsyncClient for async HTTP requests to Apollo API.
api_client = httpx.AsyncClient(
    base_url=BASE_URL,
    headers=headers
)

# --- Route Mapping ---
# RouteMap objects define which HTTP methods and URL patterns are exposed as tools.
# Here, all GET and POST requests are routed as tool endpoints.
custom_maps = [
    RouteMap(
        methods=["GET"],
        pattern=r"^.*",
        route_type=RouteType.TOOL
    ),
    RouteMap(
        methods=["POST"],
        pattern=r"^.*",
        route_type=RouteType.TOOL
    ),
]

# --- FastMCP Server Initialization ---
# Create the FastMCP server from the OpenAPI spec and HTTP client.
# The server will expose the API as a tool with the specified name and timeout.
mcp = FastMCP.from_openapi(
    openapi_spec=spec,
    client=api_client,
    name="enrichment-api-server",
    timeout=10,  # seconds
    route_maps=custom_maps,
)


@mcp.tool()
def health_check():
    """
    Health check for the enrichment API server.
    """
    return {"status": "ok", "code": 200}


# --- Entrypoint ---
# When run as a script, start the FastMCP server using SSE transport.
if __name__ == "__main__":
    print(health_check())
    mcp.run()