from fastmcp import FastMCP
import os

# Initialize the FastMCP server
mcp = FastMCP("openfda-mcp-server")

OPENFDA_BASE_URL = "https://api.fda.gov/drug"
OPENFDA_API_KEY = os.environ.get("OPENFDA_API_KEY")

@mcp.tool()
async def search_drug_label(drug_name: str, limit: int = 1) -> str:
    """
    Search OpenFDA for drug labels by drug name (generic or brand name).
    
    Args:
        drug_name: The name of the drug (e.g., 'ibuprofen', 'Advil').
        limit: Number of results to return (default 1).
    """
    async with httpx.AsyncClient() as client:
        # Sanitize input
        sanitized_name = drug_name.replace('"', "'")
        
        # Construct query: (openfda.brand_name:"drug_name" OR openfda.generic_name:"drug_name")
        query = f'(openfda.brand_name:"{sanitized_name}" openfda.generic_name:"{sanitized_name}")'
        
        params = {"search": query, "limit": limit}
        if OPENFDA_API_KEY:
            params["api_key"] = OPENFDA_API_KEY
        
        response = await client.get(
            f"{OPENFDA_BASE_URL}/label.json",
            params=params
        )
        
        if response.status_code != 200:
            return f"Error fetching drug labels: {response.status_code} - {response.text}"
        
        data = response.json()
        results = data.get("results", [])
        
        if not results:
            return f"No labels found for drug: {drug_name}"
        
        output = []
        for res in results:
            brand_name = res.get("openfda", {}).get("brand_name", ["Unknown"])[0]
            generic_name = res.get("openfda", {}).get("generic_name", ["Unknown"])[0]
            indications = res.get("indications_and_usage", ["N/A"])[0]
            dosage = res.get("dosage_and_administration", ["N/A"])[0]
            warnings = res.get("warnings", ["N/A"])[0]
            
            info = f"Brand Name: {brand_name}\nGeneric Name: {generic_name}\n\nIndications: {indications[:500]}...\n\nDosage: {dosage[:500]}...\n\nWarnings: {warnings[:500]}..."
            output.append(info)
            
        return "\n---\n".join(output)

@mcp.tool()
async def get_drug_adverse_events(drug_name: str, limit: int = 5) -> str:
    """
    Search OpenFDA for adverse events associated with a drug.
    
    Args:
        drug_name: The name of the drug.
        limit: Number of results to return (default 5).
    """
    async with httpx.AsyncClient() as client:
        # Sanitize input
        sanitized_name = drug_name.replace('"', "'")
        
        # Construct query
        query = f'patient.drug.medicinalproduct:"{sanitized_name}"'
        
        params = {"search": query, "limit": limit}
        if OPENFDA_API_KEY:
            params["api_key"] = OPENFDA_API_KEY
            
        response = await client.get(
            f"{OPENFDA_BASE_URL}/event.json",
            params=params
        )
        
        if response.status_code != 200:
            return f"Error fetching adverse events: {response.status_code} - {response.text}"
        
        data = response.json()
        results = data.get("results", [])
        
        if not results:
            return f"No adverse events found for drug: {drug_name}"
        
        output = []
        for res in results:
            reactions = [r.get("reactionmeddrapt") for r in res.get("patient", {}).get("reaction", [])]
            outcomes = res.get("patient", {}).get("reaction", [{}])[0].get("reactionoutcome", "N/A")
            seriousness = "Serious" if res.get("serious") == "1" else "Non-serious"
            
            info = f"Seriousness: {seriousness}\nReactions: {', '.join(reactions)}\nOutcome: {outcomes}"
            output.append(info)
            
        return "\n---\n".join(output)

@mcp.prompt()
def drug_safety_report(drug_name: str) -> str:
    """
    Generate a template for a drug safety report.
    """
    return f"""Please generate a comprehensive safety report for the drug "{drug_name}".

Use the `search_drug_label` tool to find official warnings and usage instructions.
Use the `get_drug_adverse_events` tool to find reported adverse events.

Structure the report as follows:
1. **Executive Summary**: Brief overview of the drug and key safety concerns.
2. **Official Warnings**: Boxed warnings, contraindications, and major precautions from the label.
3. **Reported Adverse Events**: Summary of common and serious adverse events found in the FDA database.
4. **Conclusion**: Assessment of the safety profile based on the available data.
"""

if __name__ == "__main__":
    mcp.run()
