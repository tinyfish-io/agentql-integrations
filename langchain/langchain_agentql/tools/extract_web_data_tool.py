""" AgentQL extract web data with REST API tool """

import os
from typing import Optional, Type
from typing_extensions import Self

from urllib.parse import urlparse

from langchain_core.tools import BaseTool
from langchain_core.callbacks import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from pydantic import BaseModel, Field, model_validator

from langchain_agentql.load_data import aload_data, load_data
from langchain_agentql.const import (
    DEFAULT_IS_STEALTH_MODE_ENABLED,
    DEFAULT_WAIT_FOR_PAGE_LOAD_SECONDS,
    DEFAULT_IS_SCROLL_TO_BOTTOM_ENABLED,
    DEFAULT_IS_SCREENSHOT_ENABLED,
    DEFAULT_API_TIMEOUT_SECONDS,
    DEFAULT_RESPONSE_MODE
)
from langchain_agentql.llm_descriptions import (
    EXTRACT_WEB_DATA_TOOL_DESCRIPTION,
    URL_FIELD_DESCRIPTION,
    QUERY_FIELD_DESCRIPTION,
    PROMPT_FIELD_DATA_DESCRIPTION,
)
from langchain_agentql.messages import (
    QUERY_PROMPT_REQUIRED_ERROR_MESSAGE,
    QUERY_PROMPT_EXCLUSIVE_ERROR_MESSAGE,
    UNSET_API_KEY_ERROR_MESSAGE
)


class ExtractWebDataToolInput(BaseModel):
    """Input schema for AgentQL extract web data with REST API tool."""

    url: str = Field(..., description=URL_FIELD_DESCRIPTION)
    query: Optional[str] = Field(default=None, description=QUERY_FIELD_DESCRIPTION)
    prompt: Optional[str] = Field(default=None, description=PROMPT_FIELD_DATA_DESCRIPTION)

    @model_validator(mode="after")
    @classmethod
    def validate_model(cls, model: Self) -> Self:
        """Validate URL scheme and query/prompt requirements."""
        # Validate URL scheme
        url = model.url
        if url:
            parsed_url = urlparse(url)
            if parsed_url.scheme not in ("http", "https"):
                raise ValueError("URL scheme must be 'http' or 'https'")

        # Check that query and prompt cannot be both empty or both provided
        if not model.query and not model.prompt:
            raise ValueError(QUERY_PROMPT_REQUIRED_ERROR_MESSAGE)
        if model.query and model.prompt:
            raise ValueError(QUERY_PROMPT_EXCLUSIVE_ERROR_MESSAGE)

        return model
    

class ExtractWebDataTool(BaseTool):
    """AgentQL extract web data with REST API tool.

    Setup:
        Install ``langchain-agentql`` and set environment variable ``AGENTQL_API_KEY``.

        .. code-block:: bash

            pip install -U langchain-agentql
            export AGENTQL_API_KEY="your-api-key"

    Instantiation:
        .. code-block:: python

            tool = ExtractWebDataTool()

    Invocation with args:
        .. code-block:: python

            tool.invoke({'url': 'https://www.agentql.com/blog', 'query': '{ posts[] { title }}'})

        .. code-block:: python

            {'data': 
                    {'posts': [
                        {'title': 'Launch Week Recap—make the web AI-ready'}, 
                        {'title': 'Accurate data extraction from PDFs and images with AgentQL'}, 
                        {'title': 'Introducing Scheduled Scraping Workflows'}, 
                        ...
                    ]}, 
                'metadata': {'request_id': 'xxxxxx-xxxx-xxxx-xxxx-xxxx'}
            }
    """  # noqa: E501

    name: str = "extract_web_data_with_rest_api"
    description: str = EXTRACT_WEB_DATA_TOOL_DESCRIPTION
    args_schema: Type[BaseModel] = ExtractWebDataToolInput

    api_key: Optional[str] = Field(default=None)
    """AgentQL API key. You can create one at https://dev.agentql.com."""
    timeout: int = Field(default=DEFAULT_API_TIMEOUT_SECONDS)
    """The number of seconds to wait for a request before timing out. Defaults to 900."""
    is_stealth_mode_enabled: bool = Field(default=DEFAULT_IS_STEALTH_MODE_ENABLED)
    """Whether to enable experimental anti-bot evasion strategies. This feature may not work for all websites at all times. 
    Data extraction may take longer to complete with this mode enabled. Defaults to `False`."""
    wait_for: int = Field(default=DEFAULT_WAIT_FOR_PAGE_LOAD_SECONDS)
    """The number of seconds to wait for the page to load before extracting data. Defaults to 0."""
    is_scroll_to_bottom_enabled: bool = Field(default=DEFAULT_IS_SCROLL_TO_BOTTOM_ENABLED)
    """Whether to scroll to bottom of the page before extracting data. Defaults to `False`"""
    mode: str = Field(default=DEFAULT_RESPONSE_MODE)
    """'standard' uses deep data analysis, while 'fast' trades some depth of analysis for speed and is adequate for most usecases.
    Learn more about the modes in this guide: https://docs.agentql.com/accuracy/standard-mode. Defaults to 'fast'."""
    is_screenshot_enabled: bool = Field(default=DEFAULT_IS_SCREENSHOT_ENABLED)
    """Whether to take a screenshot before extracting data. Returned in 'metadata' as a Base64 string. Defaults to `False`"""
    
    _params: dict = {}
    _metadata: dict = {}
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._params = {
            "wait_for": self.wait_for,
            "is_scroll_to_bottom_enabled": self.is_scroll_to_bottom_enabled,
            "mode": self.mode,
            "is_screenshot_enabled": self.is_screenshot_enabled,
        }
        self._metadata = {
            "experimental_stealth_mode_enabled": self.is_stealth_mode_enabled,
        }
        self._api_key = self.api_key or os.getenv("AGENTQL_API_KEY")
        if not self._api_key:
            raise ValueError(UNSET_API_KEY_ERROR_MESSAGE)
        
    def _run(
        self,
        url: str,
        query: Optional[str] = None,
        prompt: Optional[str] = None,
        _: Optional[CallbackManagerForToolRun] = None,
    ) -> dict:
        return load_data(
            url=url,
            query=query,
            prompt=prompt,
            params=self._params,
            api_key=self._api_key,
            timeout=self.timeout,
            metadata=self._metadata,
        )

    async def _arun(
        self,
        url: str,
        query: Optional[str] = None,
        prompt: Optional[str] = None,
        _: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> dict:
        return await aload_data(
            url=url,
            query=query,
            prompt=prompt,
            params=self._params,
            api_key=self._api_key,
            timeout=self.timeout,
            metadata=self._metadata,
        )
