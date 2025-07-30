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
import importlib.resources

with importlib.resources.open_text("enrichment_tools_data", "enrichment.yaml") as f:
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


mcp = FastMCP.from_openapi(
    openapi_spec=spec,
    client=api_client,
    name="enrichment-api-server",
    timeout=10,  # seconds
    route_maps=custom_maps,
)


@mcp.tool()
def apollo_api_server_health_check():
    """
    Health check for the Apollo.io API MCP server.
    """
    return {"status": "ok", "code": 200}


def main():
    try:
        mcp.run()
    except Exception as e:
        print({"status": "error", "code": 500, "message": f"Failed to start server: {str(e)}"})


if __name__ == "__main__":
    main()