# Enrichment Tools MCP Server

A FastMCP server that exposes Apollo.io enrichment APIs as MCP tools, using an OpenAPI specification. This server is designed for remote, programmatic use as a managed MCP server, and is configurable via environment variables.

---

## Features

- Exposes Apollo.io enrichment endpoints as MCP tools
- Loads OpenAPI specification from an embedded YAML file
- Supports remote configuration and deployment as an MCP server
- Secure: API credentials are provided via environment variables (`API_KEY`, `ACCESS_TOKEN`)
- Health check endpoint for server monitoring
- Built on top of FastMCP and httpx for async, robust API proxying

---

## Supported API Endpoints

The following Apollo.io enrichment APIs are exposed as MCP tools:

- **POST /api/v1/people/match** &mdash; Enrich data for a single person                       (API Reference: [https://docs.apollo.io/reference/people-enrichment])
- **POST /api/v1/organizations/enrich** &mdash; Enrich data for a single organization         (API Reference: [https://docs.apollo.io/reference/organization-enrichment])

---

## Requirements
Run as a remote host config


## Running as a Remote MCP Server

To run this server as a remote MCP server, add the following to your MCP configuration:

## MCP Client Integration

You can use this server with Cursor by adding in global `mcp.json` config

```json
{
  "mcpServers": {
    "Apollo.io": {
      "command": "uvx",
      "args": [
        "enrichment_tools"
      ],
      "env":{
        "API_KEY": "abcd",
        "ACCESS_TOKEN": "abcd"
      }
    }
  }
}
```
_Requires passing either API_KEY or ACCESS_TOKEN for authorization_

This will allow your MCP client to launch and connect to the enrichment tools server automatically.
