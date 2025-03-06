""" AgentQL extract web data from browser tool """

from typing import Optional, Type
from typing_extensions import Self

from langchain_community.tools.playwright.base import BaseBrowserTool
from langchain_core.callbacks import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from pydantic import BaseModel, Field, model_validator

from langchain_agentql.const import (
    DEFAULT_EXTRACT_DATA_TIMEOUT_SECONDS,
    DEFAULT_INCLUDE_HIDDEN_DATA,
    DEFAULT_RESPONSE_MODE,
    DEFAULT_WAIT_FOR_NETWORK_IDLE,
    REQUEST_ORIGIN
)
from langchain_agentql.utils import (
    _aget_current_agentql_page,
    _get_current_agentql_page
)
from langchain_agentql.llm_descriptions import (
    QUERY_FIELD_DESCRIPTION,
    PROMPT_FIELD_DATA_DESCRIPTION,
    EXTRACT_WEB_DATA_BROWSER_TOOL_DESCRIPTION
)
from langchain_agentql.messages import (
    QUERY_PROMPT_REQUIRED_ERROR_MESSAGE,
    QUERY_PROMPT_EXCLUSIVE_ERROR_MESSAGE,
    MISSING_BROWSER_ERROR_MESSAGE
)


class ExtractWebDataBrowserToolInput(BaseModel):
    """Input schema for AgentQL extract web data from browser tool."""

    query: Optional[str] = Field(default=None, description=QUERY_FIELD_DESCRIPTION)
    prompt: Optional[str] = Field(default=None, description=PROMPT_FIELD_DATA_DESCRIPTION)

    @model_validator(mode="after")
    @classmethod
    def check_query_and_prompt(cls, model: Self) -> Self:
        """
        Check that query and prompt cannot be both empty or both provided
        """
        if not model.query and not model.prompt:
            raise ValueError(QUERY_PROMPT_REQUIRED_ERROR_MESSAGE)
        if model.query and model.prompt:
            raise ValueError(QUERY_PROMPT_EXCLUSIVE_ERROR_MESSAGE)
        
        return model


class ExtractWebDataBrowserTool(BaseBrowserTool):
    """AgentQL extract web data from browser tool.

    Setup:
        Install ``langchain-agentql`` and set environment variable ``AGENTQL_API_KEY``.

        .. code-block:: bash

            pip install -U langchain-agentql
            export AGENTQL_API_KEY="your-api-key"

    Instantiation:
        .. code-block:: python

            # sync tool usage
            tool = ExtractWebDataBrowserTool(
                sync_browser=sync_browser,
            )

            # async tool usage
            tool = ExtractWebDataBrowserTool(
                async_browser=async_browser,
            )

    Navigate to the target page with Playwright Navigate Tool:
        .. code-block:: python

            NavigateTool(sync_browser=sync_browser).invoke({"url": "https://www.agentql.com/blog"})

    Invocation with args:
        .. code-block:: python

            tool.invoke({'query': '{ posts[] { title }}'})

        .. code-block:: python

            {'posts': [
                {'title': 'Launch Week Recap—make the web AI-ready'}, 
                {'title': 'Accurate data extraction from PDFs and images with AgentQL'}, 
                {'title': 'Introducing Scheduled Scraping Workflows'}, 
                ...
            ]}
    """  # noqa: E501

    name: str = "extract_web_data_from_browser"
    description: str = EXTRACT_WEB_DATA_BROWSER_TOOL_DESCRIPTION
    args_schema: Type[BaseModel] = ExtractWebDataBrowserToolInput

    timeout: int = Field(default=DEFAULT_EXTRACT_DATA_TIMEOUT_SECONDS)
    """The number of seconds to wait for a request before timing out. Defaults to 900."""
    wait_for_network_idle: bool = Field(default=DEFAULT_WAIT_FOR_NETWORK_IDLE)
    """Whether to wait until the network reaches a full idle state before executing. Defaults to `True`."""
    include_hidden: bool = Field(default=DEFAULT_INCLUDE_HIDDEN_DATA)
    """Whether to take into account visually hidden elements on the page. Defaults to `True`."""
    mode: str = Field(default=DEFAULT_RESPONSE_MODE)
    """'standard' uses deep data analysis, while 'fast' trades some depth of analysis for speed and is adequate for most usecases.
    Learn more about the modes in this guide: https://docs.agentql.com/accuracy/standard-mode. Defaults to 'fast'."""

    def _run(
        self,
        query: Optional[str] = None,
        prompt: Optional[str] = None,
        _: Optional[CallbackManagerForToolRun] = None,
    ) -> dict:
        if not self.sync_browser:
            raise ValueError(MISSING_BROWSER_ERROR_MESSAGE)
        
        page = _get_current_agentql_page(self.sync_browser)
        if query:
            return page.query_data(
                query,
                self.timeout,
                self.wait_for_network_idle,
                self.include_hidden,
                self.mode,
                request_origin=REQUEST_ORIGIN
            )
        elif prompt:
            return page.get_data_by_prompt_experimental(
                prompt,
                self.timeout,
                self.wait_for_network_idle,
                self.include_hidden,
                self.mode,
                request_origin=REQUEST_ORIGIN
            )

    async def _arun(
        self,
        query: Optional[str] = None,
        prompt: Optional[str] = None,
        _: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> dict:
        if not self.async_browser:
            raise ValueError(MISSING_BROWSER_ERROR_MESSAGE)
        
        page = await _aget_current_agentql_page(self.async_browser)
        if query:
            return await page.query_data(
                query,
                self.timeout,
                self.wait_for_network_idle,
                self.include_hidden,
                self.mode,
                request_origin=REQUEST_ORIGIN
            )
        elif prompt:
            return await page.get_data_by_prompt_experimental(
                prompt,
                self.timeout,
                self.wait_for_network_idle,
                self.include_hidden,
                self.mode,
                request_origin=REQUEST_ORIGIN
            )
