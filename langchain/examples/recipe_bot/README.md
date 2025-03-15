# Recipe Bot

This agent searches for a quick and simple oatmeal cookie recipe, navigates to a website with the recipe, collects the recipe ingredients and instructions, and writes it in a new CSV file `oatmeal_cookie_recipe.csv`.

## Run the script

- Install LangChain and LangGraph, OpenAI's language model, AgentQL's tools, and DuckDuckGoSearch's tools to build the agent:

```bash
pip install langchain langgraph
pip install -qU "langchain[openai]"
pip install -U langchain-agentql
pip install -U duckduckgo-search
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
python3 recipe_bot.py
```

## Learn more

- Learn more about AgentQL's <a href="https://python.langchain.com/docs/integrations/providers/agentql/" target="_blank">ExtractWebDataTool</a>, the <a href="https://python.langchain.com/api_reference/community/tools/langchain_community.tools.file_management.write.WriteFileTool.html" target="_blank">WriteFileTool</a>, and the <a href="https://python.langchain.com/docs/integrations/tools/ddg/" target="_blank">DuckDuckGoSearchResults tool</a> used in this script.
