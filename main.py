import asyncio
import httpx
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
import mcp.types as types
from pydantic import AnyUrl

# Initialize the MCP server
server = Server("openfda-mcp-server")

OPENFDA_BASE_URL = "https://api.fda.gov/drug"

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    List available tools.
    Each tool specifies its arguments using JSON Schema.
    """
    return [
        types.Tool(
            name="search_drug_label",
            description="Search OpenFDA for drug labels by drug name (generic or brand name).",
            inputSchema={
                "type": "object",
                "properties": {
                    "drug_name": {"type": "string", "description": "The name of the drug (e.g., 'ibuprofen', 'Advil')."},
                    "limit": {"type": "integer", "description": "Number of results to return (default 1).", "default": 1},
                },
                "required": ["drug_name"],
            },
        ),
        types.Tool(
            name="get_drug_adverse_events",
            description="Search OpenFDA for adverse events associated with a drug.",
            inputSchema={
                "type": "object",
                "properties": {
                    "drug_name": {"type": "string", "description": "The name of the drug."},
                    "limit": {"type": "integer", "description": "Number of results to return (default 5).", "default": 5},
                },
                "required": ["drug_name"],
            },
        ),
    ]

@server.call_tool()
async def handle_call_tool(
    name: str,
    arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    Handle tool execution requests.
    Tools can modify server state or fetch external data.
    """
    if not arguments:
        raise ValueError("Arguments are required")

    async with httpx.AsyncClient() as client:
        if name == "search_drug_label":
            drug_name = arguments.get("drug_name")
            limit = arguments.get("limit", 1)
            
            # Search drug labels
            # Construct query: openfda.brand_name:"drug_name" OR openfda.generic_name:"drug_name"
            query = f'openfda.brand_name:"{drug_name}"+openfda.generic_name:"{drug_name}"'
            url = f"{OPENFDA_BASE_URL}/label.json?search={query}&limit={limit}"
            
            response = await client.get(url)
            if response.status_code != 200:
                return [types.TextContent(type="text", text=f"Error fetching drug labels: {response.status_code} - {response.text}")]
            
            data = response.json()
            results = data.get("results", [])
            
            if not results:
                return [types.TextContent(type="text", text=f"No labels found for drug: {drug_name}")]
            
            output = []
            for res in results:
                brand_name = res.get("openfda", {}).get("brand_name", ["Unknown"])[0]
                generic_name = res.get("openfda", {}).get("generic_name", ["Unknown"])[0]
                indications = res.get("indications_and_usage", ["N/A"])[0]
                dosage = res.get("dosage_and_administration", ["N/A"])[0]
                warnings = res.get("warnings", ["N/A"])[0]
                
                info = f"Brand Name: {brand_name}\nGeneric Name: {generic_name}\n\nIndications: {indications[:500]}...\n\nDosage: {dosage[:500]}...\n\nWarnings: {warnings[:500]}..."
                output.append(info)
                
            return [types.TextContent(type="text", text="\n---\n".join(output))]

        elif name == "get_drug_adverse_events":
            drug_name = arguments.get("drug_name")
            limit = arguments.get("limit", 5)
            
            # Search adverse events
            query = f'patient.drug.medicinalproduct:"{drug_name}"'
            url = f"{OPENFDA_BASE_URL}/event.json?search={query}&limit={limit}"
            
            response = await client.get(url)
            if response.status_code != 200:
                return [types.TextContent(type="text", text=f"Error fetching adverse events: {response.status_code} - {response.text}")]
            
            data = response.json()
            results = data.get("results", [])
            
            if not results:
                return [types.TextContent(type="text", text=f"No adverse events found for drug: {drug_name}")]
            
            output = []
            for res in results:
                reactions = [r.get("reactionmeddrapt") for r in res.get("patient", {}).get("reaction", [])]
                outcomes = res.get("patient", {}).get("reaction", [{}])[0].get("reactionoutcome", "N/A")
                seriousness = "Serious" if res.get("serious") == "1" else "Non-serious"
                
                info = f"Seriousness: {seriousness}\nReactions: {', '.join(reactions)}\nOutcome: {outcomes}"
                output.append(info)
                
            return [types.TextContent(type="text", text="\n---\n".join(output))]

        else:
            raise ValueError(f"Unknown tool: {name}")

async def main():
    # Run the server using stdin/stdout streams
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="openfda-mcp-server",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())