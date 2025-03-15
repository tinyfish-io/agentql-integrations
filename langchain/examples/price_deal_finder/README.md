# Price Deal Finder

This agent navigates to an Amazon URL that displays iPad case search results, finds an iPad case that's under $25 with at least a 4.5/5 star average review, and extracts data from the web page about that product.

## Run the script

- Install LangChain and LangGraph, OpenAI's language model, and AgentQL's tools to build the agent:

```bash
pip install langchain langgraph
pip install -qU "langchain[openai]"
pip install -U langchain-agentql
```

- Configure the `AGENTQL_API_KEY` environment variable. You can get your AgentQL API key [here](https://dev.agentql.com/api-keys)

```bash
export AGENTQL_API_KEY=<YOUR_AGENTQL_API_KEY>
```

- Configure the `OPENAI_API_KEY` environment variable. You can get your OpenAI API key <a href="https://platform.openai.com/api-keys" target="_blank">here</a>

```bash
export OPENAI_API_KEY=<YOUR_OPENAI_API_KEY>
```

- Run the following command from the project's folder:

```bash
python3 price_deal_finder.py
```

## Learn more

- Learn more about AgentQL's <a href="https://python.langchain.com/docs/integrations/providers/agentql/" target="_blank">ExtractWebDataTool</a> and the <a href="https://python.langchain.com/docs/integrations/tools/playwright/" target="_blank">Playwright tools</a> used in this script.
