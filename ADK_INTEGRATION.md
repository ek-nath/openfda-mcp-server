# Integration with Google Gen AI ADK

This guide explains how to use the OpenFDA MCP server within an agent built using the [Google Gen AI Agent Development Kit (ADK)](https://github.com/googleapis/genai-toolbox).

The ADK supports MCP via the `McpToolset` class, allowing your agent to connect to this server and use its tools (`search_drug_label`, `get_drug_adverse_events`) natively.

## Prerequisites

- Python 3.9+
- Google ADK installed: `pip install google-adk` (or via `uv add google-adk`)
- The `openfda-mcp-server` repository cloned locally.

## integration Pattern: ADK as MCP Client

You will configure your ADK agent to spawn the OpenFDA MCP server as a subprocess using `uv`.

### Example Agent Code

Create a file named `agent.py`:

```python
import os
import asyncio
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters
from google.genai import types

# Load environment variables (e.g., GOOGLE_API_KEY)
load_dotenv()

# --- Configuration ---
# Set this to the absolute path of your openfda-mcp-server directory
MCP_SERVER_DIR = os.path.abspath("./openfda-mcp-server") 

async def main():
    # 1. Define the MCP Toolset
    # This tells ADK how to launch our server using 'uv'
    openfda_toolset = McpToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command="uv",
                args=[
                    "--directory", 
                    MCP_SERVER_DIR, 
                    "run", 
                    "--quiet", 
                    "server.py"
                ],
            )
        )
    )

    # 2. Create the Agent
    agent = LlmAgent(
        model="gemini-2.0-flash",
        name="pharma_assistant",
        instruction="""
        You are a pharmaceutical safety assistant. 
        Use the OpenFDA tools to answer questions about drug labels and adverse events.
        Always verify warnings before giving advice.
        """,
        tools=[openfda_toolset]
    )

    # 3. Create a Runner and Session
    runner = Runner(
        agent=agent,
        session_service=InMemorySessionService()
    )
    
    session = await runner.session_service.create_session(
        state={}, app_name="pharma_app", user_id="user_1"
    )

    # 4. Run a Query
    query = "Are there any serious adverse events reported for Aspirin recently?"
    print(f"User: {query}")
    
    response_stream = runner.run_async(
        session_id=session.id, 
        user_id=session.user_id, 
        new_message=types.Content(role="user", parts=[types.Part(text=query)])
    )

    print("Agent:")
    async for event in response_stream:
        # Check for tool calls or text responses in the event structure
        # (Simplified printing for demonstration)
        if hasattr(event, 'content') and event.content:
            for part in event.content.parts:
                if part.text:
                    print(part.text, end="", flush=True)
    print("\n")

    # 5. Cleanup
    await openfda_toolset.close()

if __name__ == "__main__":
    asyncio.run(main())
```

### Key Components

1.  **`McpToolset`**: Acts as the bridge. It connects to the MCP server and converts the MCP tools into ADK-compatible tools.
2.  **`StdioServerParameters`**: Configures the command to launch the server.
    *   `command="uv"`: We use `uv` to ensure the server runs in its own isolated environment with the correct dependencies.
    *   `args=[...]`: We pass `--directory` to ensure `uv` finds the `pyproject.toml` of the server, and `--quiet` to prevent `uv` logs from interfering with the MCP protocol.

### Deploying to Production

When deploying your agent (e.g., to Cloud Run), you should ensure the `McpToolset` is defined synchronously within your agent definition if required by your specific deployment pipeline, or consider running the MCP server as a separate microservice and connecting via SSE (`SseConnectionParams`) instead of Stdio.

For containerized deployments, you can bundle the MCP server code into the same Docker image and point the `args` to the local path within the container.

