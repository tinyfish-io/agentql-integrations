# Human Fallback Scraper

This example extracts company data from Y Combinator's company directory. If AgentQL's automated extraction fails (e.g., due to anti-bot measures), the task is automatically delegated to a human worker on [Human Pages](https://humanpages.ai).

## Run the script

- Install the AgentQL Human Pages integration:

```bash
pip install agentql-humanpages
```

- Configure the `AGENTQL_API_KEY` environment variable. You can get your AgentQL API key [here](https://dev.agentql.com/api-keys)

```bash
export AGENTQL_API_KEY=<YOUR_AGENTQL_API_KEY>
```

- Configure the `HUMANPAGES_API_KEY` environment variable. You can get your Human Pages API key at [humanpages.ai](https://humanpages.ai)

```bash
export HUMANPAGES_API_KEY=<YOUR_HUMANPAGES_API_KEY>
```

- Run the following command from the project's folder:

```bash
python3 human_fallback_scraper.py
```

## How it works

1. The `HumanFallbackAgent` first attempts to extract data using AgentQL's REST API.
2. If extraction fails (HTTP error, timeout, empty results), the agent automatically:
   - Searches for an available human worker on Human Pages
   - Creates a job with the extraction task description
   - Polls for completion and returns the results
3. The returned result includes a `source` field indicating whether data came from `"agentql"` or `"humanpages"`.

## Learn more

- [AgentQL Documentation](https://docs.agentql.com/)
- [Human Pages API](https://humanpages.ai)
