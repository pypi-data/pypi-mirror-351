# Enrichment Tools MCP Server

This project provides a FastMCP server that exposes Apollo.io enrichment APIs as tools, using an OpenAPI specification. It can be run as a server or as a standalone tool, and is configurable via environment variables.

## Features
- Exposes Apollo.io enrichment endpoints as MCP tools
- Loads OpenAPI spec from `specs/enrichment.yaml`
- Supports both server and standalone usage
- Configurable via environment variables (`API_KEY`, `ACCESS_TOKEN`)

## Requirements
- Python 3.9+
- Dependencies (see `pyproject.toml`):
  - fastmcp==2.5.2
  - mcp>=1.2.0
  - requests
  - beautifulsoup4

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd api-mcp
   ```
2. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. **Install dependencies:**
   ```bash
   pip install -e .
   ```

## Configuration

- **API Credentials:**
  - Set `API_KEY` (and/or `ACCESS_TOKEN`) in your environment:
    ```bash
    export API_KEY=your_apollo_api_key
    export ACCESS_TOKEN=your_apollo_access_token  # optional
    ```
- **OpenAPI Spec:**
  - The server loads the OpenAPI spec from `specs/enrichment.yaml`.

## Usage

### As a Server

Run the server directly:
```bash
export API_KEY=your_apollo_api_key
python3 src/enrichment_tools.py
```

Or, if installed as a package (via pip):
```bash
enrichment-tools
```

This will start a FastMCP server using Server-Sent Events (SSE) transport, exposing the Apollo.io enrichment API as MCP tools.


### As a Standalone MCP Server (Subprocess Example) (Remote Server)
```json
"apollo_io_enrichment_tools": {
  "command": "uvx",
  "args": [        
    "enrichment-tools"
  ]
}
```


### As a Standalone Tool (Subprocess Example) (Local Subprocess)

You can invoke the tool as a subprocess, for example:
```json
"enrichmentToolPy":{
  "command": "/absolute/path/to/python3", 
  "args": ["/absolute/path/to/enrichment_tools.py"],
  "env": {
    "API_KEY": "xyz"
  }
}
```
Replace the paths and API key as appropriate for your environment.

## API Endpoints

The following endpoints are exposed (see `specs/enrichment.yaml` for full details):

- **GET /api/v1/people/match**: Enrich data for a single person. Query params include `first_name`, `last_name`, `email`, `organization_name`, `domain`, `linkedin_url`, etc.
- **GET /api/v1/organizations/enrich**: Enrich data for a single organization. Query param: `domain` (required).

## Development

- To modify the OpenAPI spec, edit `specs/enrichment.yaml`.
- To add new endpoints, update the spec and restart the server.
- The main server logic is in `src/enrichment_tools.py`.

## License
MIT

## Authors
- Kavya-24 (<kavya.goyal@apollo.io>)
