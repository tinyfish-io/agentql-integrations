"""Example: Extract product data with AgentQL, falling back to Human Pages.

This script demonstrates using the HumanFallbackAgent to extract structured
product data from a web page. If AgentQL cannot extract the data (due to
anti-bot protections, CAPTCHAs, or other issues), the task is automatically
delegated to a human worker on Human Pages.

Prerequisites:
    pip install agentql-humanpages

Environment variables:
    AGENTQL_API_KEY   - Your AgentQL API key (https://dev.agentql.com)
    HUMANPAGES_API_KEY - Your Human Pages API key (https://humanpages.ai)
"""

import json

from agentql_humanpages import HumanFallbackAgent

# Initialize the agent with both API keys (reads from env vars by default)
agent = HumanFallbackAgent()

# Define the target URL and the data to extract
url = "https://www.ycombinator.com/companies"
query = """
{
    companies[] {
        name
        description
        batch
        location
    }
}
"""

# Extract data -- AgentQL tries first, Human Pages is the fallback
result = agent.extract(url=url, query=query)

# Check which source provided the data
if result["source"] == "agentql":
    print("Data extracted via AgentQL:")
    print(json.dumps(result["data"], indent=2))
else:
    print(f"Data extracted via Human Pages (job ID: {result['job_id']}):")
    print(f"Job status: {result['status']['status']}")
    for message in result["messages"]:
        print(f"  Message: {message.get('content', '')}")
