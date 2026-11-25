# agentql-humanpages

An integration package connecting [AgentQL](https://www.agentql.com/) and [Human Pages](https://humanpages.ai) for human-in-the-loop web data extraction.

When AgentQL's automated extraction fails -- due to anti-bot protections, CAPTCHAs, empty results, or any other blocker -- the task is automatically delegated to a human worker via the Human Pages platform.

## Installation

```bash
pip install -U agentql-humanpages
```

You need to configure both API keys:

- `AGENTQL_API_KEY` -- get one from the [AgentQL Dev Portal](https://dev.agentql.com)
- `HUMANPAGES_API_KEY` -- get one from [Human Pages](https://humanpages.ai)

## Quick Start

```python
from agentql_humanpages import HumanFallbackAgent

agent = HumanFallbackAgent(
    agentql_api_key="your-agentql-key",
    humanpages_api_key="your-humanpages-key",
)

result = agent.extract(
    url="https://example.com/products",
    query="{ products[] { name price } }",
)

if result["source"] == "agentql":
    print("Extracted via AgentQL:", result["data"])
else:
    print("Extracted via human:", result["messages"])
```

## HumanFallbackAgent

The main entry point. Attempts AgentQL extraction first, then falls back to Human Pages.

```python
agent = HumanFallbackAgent(
    agentql_api_key="...",       # or set AGENTQL_API_KEY env var
    humanpages_api_key="...",    # or set HUMANPAGES_API_KEY env var
    price_usdc=5.0,              # default price for human jobs
    deadline_hours=24,           # default deadline for human jobs
)
```

### extract()

```python
result = agent.extract(
    url="https://example.com",
    query="{ products[] { name price } }",  # AgentQL query
    # OR
    prompt="Get all product names and prices",  # Natural language
    fallback_description="Custom instructions for the human worker",
    price_usdc=10.0,       # override default price
    deadline_hours=12,     # override default deadline
)
```

Returns a dict with:
- `source`: `"agentql"` or `"humanpages"`
- `data`: extracted data (when source is agentql)
- `job_id`, `status`, `messages`: job details (when source is humanpages)

### aextract()

Async version of `extract()` with the same interface.

## HumanPagesClient

Lower-level client for the Human Pages REST API:

```python
from agentql_humanpages import HumanPagesClient

client = HumanPagesClient(api_key="your-key")

# Search for available humans
humans = client.search_humans(skill="web task", available=True)

# Create a job
job = client.create_job(
    human_id=humans[0]["id"],
    title="Extract product data",
    description="Visit example.com and extract all product names and prices.",
    price_usdc=5.0,
    deadline_hours=24,
)

# Check job status
status = client.get_job_status(job["id"])

# Get messages
messages = client.get_job_messages(job["id"])
```

All methods have async counterparts (`asearch_humans`, `acreate_job`, `aget_job_status`, `aget_job_messages`).

## Run Tests

Unit tests (no network calls):

```bash
make test
```

Integration tests (requires valid API keys):

```bash
make integration_tests
```
