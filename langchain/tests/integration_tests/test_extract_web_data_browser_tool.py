import pytest
from langchain_community.tools.playwright.navigate import NavigateTool
from langchain_openai import ChatOpenAI

from langchain_agentql.tools import ExtractWebDataBrowserTool
from langchain_agentql.utils import create_async_playwright_browser

from .test_data import TEST_DATA, TEST_QUERY, TEST_URL


class TestExtractWebDataBrowserToolCall:
    @pytest.fixture(autouse=True)
    async def browser_tool(self):
        async_browser = await create_async_playwright_browser(headless=True)
        navigate_tool = NavigateTool(async_browser=async_browser)
        await navigate_tool.arun({"url": TEST_URL})
        tool = ExtractWebDataBrowserTool(async_browser=async_browser)
        yield tool
        await async_browser.close()

    @pytest.fixture()
    def llm(self, browser_tool):
        llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
        )
        return llm.bind_tools([browser_tool])

    async def test_extract_web_data_browser_tool_invoke(self, browser_tool):
        res = await browser_tool.ainvoke(
            {"query": TEST_QUERY, "prompt": None}
        )
        assert res == TEST_DATA

    async def test_extract_web_data_browser_llm_tool_call(self, llm):
        msg = await llm.ainvoke(
            f"Extract the data from the current web page using the following agentql query: {TEST_QUERY}"
        )
        tool_call_args_1 = {"query": TEST_QUERY, "prompt": None}
        tool_call_args_2 = {"query": TEST_QUERY}

        assert msg.tool_calls[0]["args"] in [tool_call_args_1, tool_call_args_2]
