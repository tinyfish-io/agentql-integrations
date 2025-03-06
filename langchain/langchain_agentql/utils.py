from typing import Optional, List, TYPE_CHECKING

import agentql
from langchain_community.tools.playwright.utils import (
    aget_current_page,
    get_current_page
)
from langchain_community.tools.playwright.utils import create_sync_playwright_browser as create_sync_playwright_browser_from_tools

try:
    from playwright.async_api import Browser as AsyncBrowser
    from playwright.async_api import Page as AsyncPage
    from playwright.sync_api import Browser as SyncBrowser
    from playwright.sync_api import Page as SyncPage
except ImportError as e:
    raise ImportError(
        "Unable to import playwright. Please make sure playwright module is properly installed."
    ) from e

def _get_current_agentql_page(browser: SyncBrowser) -> SyncPage:
    """
    Get the current page of the browser.
    Args:
        browser: The browser to get the current page from.
    Returns:
        Page: The current page.
    """
    return agentql.wrap(get_current_page(browser))


async def _aget_current_agentql_page(browser: AsyncBrowser) -> AsyncPage:
    """
    Get the current page of the browser.
    Args:
        browser: The browser to get the current page from.
    Returns:
        Page: The current page.
    """
    return await agentql.wrap_async(await aget_current_page(browser))


def create_sync_playwright_browser(
    headless: bool = True, args: Optional[List[str]] = None
) -> SyncBrowser:
    """
    Create a sync playwright browser.
    Args:
        headless: Whether to run the browser in headless mode. Defaults to True.
        args: arguments to pass to browser.chromium.launch
    Returns:
        Browser: The playwright browser.
    """
    return create_sync_playwright_browser_from_tools(headless=headless, args=args)

# Note: playwright's create_async_playwright_browser() function does not work properly
# https://github.com/langchain-ai/langchain/issues/15605

async def create_async_playwright_browser(
    headless: bool = True, args: Optional[List[str]] = None
) -> AsyncBrowser:
    """
    Create an async playwright browser.
    Args:
        headless: Whether to run the browser in headless mode. Defaults to True.
        args: arguments to pass to browser.chromium.launch
    Returns:
        Browser: The playwright browser.
    """
    from playwright.async_api import async_playwright

    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=headless, args=args)
    return browser
