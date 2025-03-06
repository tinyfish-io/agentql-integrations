""" AgentQL get web element from browser tool """

from typing import Optional, Type

from langchain_community.tools.playwright.base import BaseBrowserTool
from langchain_core.callbacks import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from pydantic import BaseModel, Field

from langchain_agentql.const import (
    DEFAULT_EXTRACT_ELEMENTS_TIMEOUT_SECONDS,
    DEFAULT_INCLUDE_HIDDEN_ELEMENTS,
    DEFAULT_RESPONSE_MODE,
    DEFAULT_WAIT_FOR_NETWORK_IDLE,
    REQUEST_ORIGIN
)
from langchain_agentql.utils import (
    _aget_current_agentql_page,
    _get_current_agentql_page
)
from langchain_agentql.messages import MISSING_BROWSER_ERROR_MESSAGE
from langchain_agentql.llm_descriptions import (
    GET_WEB_ELEMENT_BROWSER_TOOL_DESCRIPTION,
    PROMPT_FIELD_ELEMENT_DESCRIPTION
)


class GetWebElementBrowserToolInput(BaseModel):
    """Input schema for AgentQL get web element from browser tool."""

    prompt: str = Field(..., description=PROMPT_FIELD_ELEMENT_DESCRIPTION)


class GetWebElementBrowserTool(BaseBrowserTool):
    """AgentQL get web element from browser tool.

    Setup:
        Install ``langchain-agentql`` and set environment variable ``AGENTQL_API_KEY``.

        .. code-block:: bash

            pip install -U langchain-agentql
            export AGENTQL_API_KEY="your-api-key"

    Instantiation:
        .. code-block:: python

            # sync tool usage
            tool = GetWebElementBrowserTool(
                sync_browser=sync_browser,
            )

            # async tool usage
            tool = GetWebElementBrowserTool(
                async_browser=async_browser,
            )

    Navigate to the target page with Playwright Navigate Tool:
        .. code-block:: python

            NavigateTool(sync_browser=sync_browser).invoke({"url": "https://www.agentql.com/blog"})

    Invocation with args:
        .. code-block:: python

            selector = tool.invoke({'prompt': 'The next page navigation button'})

        .. code-block:: python

            "[tf623_id='191']"
    
    Usage with Playwright Click Tool:
        .. code-block:: python

            ClickTool(async_browser=async_browser, visible_only=False).invoke({'selector': selector})
    """  # noqa: E501

    name: str = "get_web_element_from_browser"
    description: str = GET_WEB_ELEMENT_BROWSER_TOOL_DESCRIPTION
    args_schema: Type[BaseModel] = GetWebElementBrowserToolInput

    timeout: int = DEFAULT_EXTRACT_ELEMENTS_TIMEOUT_SECONDS
    """The number of seconds to wait for a request before timing out. Defaults to 300."""
    wait_for_network_idle: bool = DEFAULT_WAIT_FOR_NETWORK_IDLE
    """Whether to wait until the network reaches a full idle state before executing. Defaults to `True`."""
    include_hidden: bool = DEFAULT_INCLUDE_HIDDEN_ELEMENTS
    """Whether to take into account visually hidden elements on the page. Defaults to `False`."""
    mode: str = DEFAULT_RESPONSE_MODE
    """'standard' uses deep data analysis, while 'fast' trades some depth of analysis for speed and is adequate for most usecases.
    Learn more about the modes in this guide: https://docs.agentql.com/accuracy/standard-mode. Defaults to 'fast'."""

    def _run(
        self, 
        prompt: str, 
        _: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        if not self.sync_browser:
            raise ValueError(MISSING_BROWSER_ERROR_MESSAGE)
        
        page = _get_current_agentql_page(self.sync_browser)
        element = page.get_by_prompt(
            prompt,
            self.timeout,
            self.wait_for_network_idle,
            self.include_hidden,
            self.mode,
            request_origin=REQUEST_ORIGIN
        )
        tf_id = element.get_attribute("tf623_id")
        return f"[tf623_id='{tf_id}']"

    async def _arun(
        self, 
        prompt: str, 
        _: Optional[AsyncCallbackManagerForToolRun] = None
    ) -> str:
        if not self.async_browser:
            raise ValueError(MISSING_BROWSER_ERROR_MESSAGE)
        
        page = await _aget_current_agentql_page(self.async_browser)
        element = await page.get_by_prompt(
            prompt,
            self.timeout,
            self.wait_for_network_idle,
            self.include_hidden,
            self.mode,
            request_origin=REQUEST_ORIGIN
        )
        tf_id = await element.get_attribute("tf623_id")
        return f"[tf623_id='{tf_id}']"
