# openfda-mcp-server

An MCP (Model Context Protocol) server for the OpenFDA API.

## Features

- **search_drug_label**: Search for drug labels by brand or generic name.
- **get_drug_adverse_events**: Search for adverse events associated with a specific drug.

## Setup

1. Install dependencies:
   ```bash
   uv sync
   ```

2. Run the server:
   ```bash
   uv run main.py
   ```

## Integration with Claude Desktop

Add the following to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "openfda": {
      "command": "uv",
      "args": [
        "--directory",
        "/Users/ek/Projects/openfda-mcp-server",
        "run",
        "main.py"
      ]
    }
  }
}
```

## API Documentation

This server uses the [OpenFDA API](https://open.fda.gov/apis/).
