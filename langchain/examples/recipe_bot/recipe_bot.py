import asyncio

from langchain.chat_models import init_chat_model
from langchain_agentql import AgentQLBrowserToolkit
from langchain_agentql.utils import create_async_playwright_browser
from langchain_community.tools import DuckDuckGoSearchResults
from langchain_community.tools.file_management.write import WriteFileTool
from langchain_community.tools.playwright import ClickTool, NavigateTool
from langgraph.prebuilt import create_react_agent


async def main():

    # Instantiate LLM
    model = init_chat_model("gpt-4o-mini", model_provider="openai")

    # Create Playwright browser instance
    async_agent_browser = await create_async_playwright_browser(headless=True)

    # Get tools
    agentql_toolkit = AgentQLBrowserToolkit(async_browser=async_agent_browser)

    search_write_tools = [
        DuckDuckGoSearchResults(output_format="list"),
        WriteFileTool(),
    ]

    playwright_toolkit = [
        NavigateTool(async_browser=async_agent_browser),
        ClickTool(async_browser=async_agent_browser, visible_only=False),
    ]

    # Create agent
    agent_executor = create_react_agent(
        model, agentql_toolkit.get_tools() + playwright_toolkit + search_write_tools
    )

    prompt = """
    Search for an easy and quick recipe for baking oatmeal cookies. From one of the links, extract the ingredients needed and instructions and put them into a CSV file 'oatmeal_cookie_recipe.csv'.
    """

    # Execute agent
    events = agent_executor.astream(
        {"messages": [("user", prompt)]},
        stream_mode="values",
    )

    async for event in events:
        event["messages"][-1].pretty_print()


asyncio.run(main())
