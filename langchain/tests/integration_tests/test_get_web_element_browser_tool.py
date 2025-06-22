import pytest
from langchain_community.tools.playwright import NavigateTool

from langchain_agentql.tools import GetWebElementBrowserTool
from langchain_agentql.utils import create_async_playwright_browser

from .test_data import TEST_URL

class TestGetWebElementBrowserToolCall:
    @pytest.fixture(autouse=True)
    async def browser_tool(self):
        async_browser = await create_async_playwright_browser(headless=True)
        navigate_tool = NavigateTool(async_browser=async_browser)
        await navigate_tool.arun({"url": TEST_URL})
        get_web_element_browser_tool = GetWebElementBrowserTool(async_browser=async_browser)
        yield get_web_element_browser_tool
        await async_browser.close()

    async def test_get_web_element_browser_tool_invoke(self, browser_tool):
        res = await browser_tool.ainvoke(
            {"prompt": "button for buying it now"}
        )
        assert res == "[tf623_id='963']"
