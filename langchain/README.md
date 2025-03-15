# langchain-agentql

[AgentQL](https://www.agentql.com/) provides web interaction and structured data extraction from any web page using an [AgentQL query](https://docs.agentql.com/agentql-query) or a Natural Language prompt. AgentQL can be used across multiple languages and web pages without breaking over time and change.

## Installation

```bash
pip install -U langchain-agentql
```

You also need to configure the `AGENTQL_API_KEY` environment variable. You can acquire an API key from our [Dev Portal](https://dev.agentql.com).

## Document Loader

AgentQLLoader is a document loader that uses [AgentQL query](https://docs.agentql.com/agentql-query) to extract structured data from a web page.

```python
from langchain_agentql.document_loaders import AgentQLLoader

loader = AgentQLLoader(
    url="https://www.agentql.com/blog",
    query="""
    {
        posts[] {
            title
            url
            date
            author
        }
    }
    """,
    is_scroll_to_bottom_enabled=True
)
docs = loader.load()
```

You can learn more about how to use AgentQLLoader in this [Jupyter notebook](https://github.com/tinyfish-io/agentql-integrations/blob/main/langchain/docs/document_loaders.ipynb).

## Tools/Toolkits

AgentQL provides the following three tools:

- **`ExtractWebDataTool`**: Extracts structured data as JSON from a web page given a URL using either an [AgentQL query](https://docs.agentql.com/agentql-query/query-intro) or a Natural Language description of the data.

- **`ExtractWebDataBrowserTool`**: Extracts structured data as JSON from the active web page in a browser using either an [AgentQL query](https://docs.agentql.com/agentql-query/query-intro) or a Natural Language description. **This tool must be used with a Playwright browser.**

- **`GetWebElementBrowserTool`**: Finds a web element on the active web page in a browser using a Natural Language description and returns its CSS selector for further interaction. **This tool must be used with a Playwright browser.**

We also provide an `AgentQLBrowserToolkit` toolkit with both `ExtractWebDataBrowserTool` and `GetWebElementBrowserTool` browser tools bundled.

You can learn more about how to use AgentQL tools in this [Jupyter notebook](https://github.com/tinyfish-io/agentql-integrations/blob/main/langchain/docs/tools.ipynb).

### Extract data using REST API

```python
from langchain_agentql.tools import ExtractWebDataTool

extract_web_data_tool = ExtractWebDataTool()
extract_web_data_tool.invoke({
    'url': 'https://www.agentql.com/blog', 
    'query': '{ posts[] { title url date author } }', 
})
```

### Work with data and web elements using browser

#### Setup

In order to use the `ExtractWebDataBrowserTool` and `GetWebElementBrowserTool`, you need to have a Playwright browser instance. If you do not have an active instance, you can initiate one using the `create_async_playwright_browser` or `create_sync_playwright_browser` methods:

```python
from langchain_agentql.utils import create_async_playwright_browser
async_browser = await create_async_playwright_browser()
```

You can also use an existing browser instance via Chrome DevTools Protocol (CDP) connection URL:

```python
p = await async_playwright().start()
async_browser = await p.chromium.connect_over_cdp("CDP_CONNECTION_URL")
```
#### Extract data from the active browser page

```python
from langchain_agentql.tools import ExtractWebDataBrowserTool

extract_web_data_browser_tool = ExtractWebDataBrowserTool(async_browser=async_browser)
json_data = await extract_web_data_browser_tool.ainvoke({'prompt': 'The blog posts with title, url, date of post and author'})
```

#### Find a web element on the active browser page

```python
from langchain_agentql.tools import GetWebElementBrowserTool

get_web_element_browser_tool = GetWebElementBrowserTool(async_browser=async_browser)
selector = await get_web_element_browser_tool.ainvoke({'prompt': 'The next page navigation button'})
```

## Agentic Usage

This tool has a more extensive example for agentic usage documented in this [Jupyter notebook](./docs/tools.ipynb)

## Run Tests

In order to run integration tests, you need to configure LLM credentials by setting the `OPENAI_API_KEY` environment variables first. Then run the tests with the following command:

```bash
make integration_tests
```
