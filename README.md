# OpenFDA MCP Server

An MCP (Model Context Protocol) server for the [OpenFDA API](https://open.fda.gov/apis/), built with [FastMCP](https://github.com/jlowin/fastmcp). This server exposes FDA drug labels and adverse event data to LLMs via the Model Context Protocol.

## Features

### Tools
- **`search_drug_label`**: Search for official FDA drug labels by brand or generic name. Returns indications, warnings, and dosage information.
- **`get_drug_adverse_events`**: Search for reported adverse events associated with a specific drug, including seriousness and outcomes.

### Prompts
- **`drug_safety_report`**: A prompt template that guides the LLM to generate a comprehensive safety report for a specific drug, combining label warnings with real-world adverse event data.

## Installation & Setup

1.  **Clone and Install:**
    ```bash
    git clone https://github.com/ek-nath/openfda-mcp-server.git
    cd openfda-mcp-server
    uv sync
    ```

2.  **Verify Installation:**
    Run the server manually to ensure dependencies are correct (it will wait for input):
    ```bash
    uv run server.py
    ```

## Integration

### 1. Gemini CLI

To use this tool with the [Gemini CLI](https://gemini-cli.com), add the server configuration to your global settings file (`~/.gemini/settings.json`).

**Configuration:**

```json
{
  "mcpServers": {
    "openfda": {
      "command": "uv",
      "args": [
        "--directory",
        "/ABSOLUTE/PATH/TO/openfda-mcp-server",
        "run",
        "--quiet",
        "server.py"
      ]
    }
  }
}
```
*Replace `/ABSOLUTE/PATH/TO/...` with the full path to your cloned directory.*

**Troubleshooting:**
If you encounter `EPERM` errors on macOS regarding `.Trash`, add `.Trash/` to your `~/.geminiignore` file.

### 2. Google ADK (Agent Development Kit)

This server can be easily integrated into Python agents built with the [Google Gen AI Agent Development Kit (ADK)](https://github.com/googleapis/genai-toolbox).

👉 **[View the ADK Integration Guide](ADK_INTEGRATION.md)**

### 3. Claude Desktop

Add the same configuration snippet above to your `claude_desktop_config.json` (usually located in `~/Library/Application Support/Claude/`).

## Usage Examples

Once connected, you can ask your agent questions like:
- "Check the official FDA label for Lisinopril. Are there warnings about kidney issues?"
- "I take Atorvastatin. Is it safe to take Ibuprofen?"
- "Generate a drug safety report for Metformin."

## License

MIT