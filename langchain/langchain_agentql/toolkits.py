""" AgentQL toolkit """

from typing import List

from langchain_community.agent_toolkits.playwright.toolkit import (
    PlayWrightBrowserToolkit,
)
from langchain_core.tools import BaseTool

from langchain_agentql.tools import (
    ExtractWebDataBrowserTool,
    GetWebElementBrowserTool
)


class AgentQLBrowserToolkit(PlayWrightBrowserToolkit):
    """AgentQL toolkit.

    Setup:
        Install ``langchain-agentql`` and set environment variable ``AGENTQL_API_KEY``.

        .. code-block:: bash

            pip install -U langchain-agentql
            export AGENTQL_API_KEY="your-api-key"

    Key init args:
        sync_browser: Optional[SyncBrowser]
            A synchronous browser instance for executing tools synchronously
        async_browser: Optional[AsyncBrowser]
            An asynchronous browser instance for executing tools asynchronously

    Instantiate:
        .. code-block:: python

            from langchain-agentql import AgentQLBrowserToolkit

            toolkit = AgentQLBrowserToolkit(
                sync_browser=sync_browser
            )

            or

            toolkit = AgentQLBrowserToolkit.from_browser(
                sync_browser=sync_browser
            )

    Tools:
        .. code-block:: python

            agentql_tools = toolkit.get_tools()

        .. code-block:: none

            [ExtractWebDataBrowserTool(sync_browser=<Browser type=<BrowserType name=chromium ...>),
            GetWebElementBrowserTool(sync_browser=<Browser type=<BrowserType name=chromium ...>)]

    Use within an agent (Must use async browser):
        .. code-block:: python

            from langgraph.prebuilt import create_react_agent

            # Add Playwright Navigation Tool to agent's tools
            navigate_tool = NavigateTool(async_browser=async_browser)
            browser_agent_tools = toolkit.get_tools() + [navigate_tool]

            # Query the data
            agent_executor = create_react_agent(llm, browser_agent_tools)

            prompt = "Extract the data from https://www.agentql.com/blog using the following AgentQL query: { pokemons[] { name price }}"

            events = agent_executor.astream(
                {"messages": [("user", prompt)]},
                stream_mode="values",
            )
            async for event in events:
                event["messages"][-1].pretty_print()

        .. code-block:: none

            ================================ Human Message =================================
            Extract the data from https://www.agentql.com/blog using the following AgentQL query: { posts[] { title }}
            ================================== Ai Message ==================================
            Tool Calls:
            navigate_browser (call_XXXX)
            Call ID: call_XXXX
            Args:
                url: https://www.agentql.com/blog
            ================================= Tool Message =================================
            Name: navigate_browser

            Navigating to https://www.agentql.com/blog returned status code 200
            ================================== Ai Message ==================================
            Tool Calls:
            extract_web_data_from_browser (call_XXXX)
            Call ID: call_XXXX
            Args:
                query: { posts[] { title }}
            ================================= Tool Message =================================
            Name: extract_web_data_from_browser

            {"posts": [
                {"title": "Launch Week Recap—make the web AI-ready"}, 
                {"title": "Automated web application testing with AI and Playwright"},
                ...
            ]}
            ================================== Ai Message ==================================
            Here are the titles of the blog posts extracted from the AgentQL blog:

            1. Launch Week Recap—make the web AI-ready
            2. Automated web application testing with AI and Playwright
            ...
    """  # noqa: E501

    def get_tools(self) -> List[BaseTool]:
        """Get the tools in the toolkit."""
        return [
          ExtractWebDataBrowserTool.from_browser(sync_browser=self.sync_browser, async_browser=self.async_browser),
          GetWebElementBrowserTool.from_browser(sync_browser=self.sync_browser, async_browser=self.async_browser)
        ]
