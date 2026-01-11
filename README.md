# openfda-mcp-server

An MCP (Model Context Protocol) server for the OpenFDA API, built with [FastMCP](https://github.com/jlowin/fastmcp).

## Features

### Tools
- **search_drug_label**: Search for drug labels by brand or generic name.
- **get_drug_adverse_events**: Search for adverse events associated with a specific drug.

### Prompts
- **drug_safety_report**: Generates a prompt template for creating a comprehensive safety report for a specific drug.

## Setup

1. Install dependencies:
   ```bash
   uv sync
   ```

2. Run the server:
   ```bash
   uv run server.py
   ```

## Integration with Gemini CLI / Claude Desktop

Add the following to your settings file (e.g., `~/.gemini/settings.json` or `claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "openfda": {
      "command": "uv",
      "args": [
        "--directory",
        "/Users/ek/Projects/openfda-mcp-server",
        "run",
        "--quiet",
        "server.py"
      ]
    }
  }
}
```

## API Documentation

This server uses the [OpenFDA API](https://open.fda.gov/apis/).
