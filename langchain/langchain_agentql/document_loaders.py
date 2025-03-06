"""AgentQL document loader."""

import os
from typing import Iterator, Optional

from langchain_core.document_loaders.base import BaseLoader
from langchain_core.documents import Document

from langchain_agentql.const import DEFAULT_API_TIMEOUT_SECONDS
from langchain_agentql.load_data import load_data

from langchain_agentql.const import (
    DEFAULT_IS_STEALTH_MODE_ENABLED,
    DEFAULT_WAIT_FOR_PAGE_LOAD_SECONDS,
    DEFAULT_IS_SCROLL_TO_BOTTOM_ENABLED,
    DEFAULT_IS_SCREENSHOT_ENABLED,
    DEFAULT_RESPONSE_MODE,
)
from langchain_agentql.messages import UNSET_API_KEY_ERROR_MESSAGE


class AgentQLLoader(BaseLoader):
    """AgentQL document loader.

    Setup:
        Install ``langchain-agentql`` and set environment variable ``AGENTQL_API_KEY``.
        You can get API key from our Dev Portal: https://dev.agentql.com/

        .. code-block:: bash

            pip install -U langchain-agentql
            export AGENTQL_API_KEY="your-api-key"

    Instantiate:
        .. code-block:: python

            from langchain_community.document_loaders import AgentQLLoader

            loader = AgentQLLoader(
                url = "https://www.agentql.com/blog",
                query = "{ posts[] { title url date author } }",
                is_scroll_to_bottom_enabled = True
                # To learn all the params and their specs, visit: https://docs.agentql.com/rest-api/api-reference
            )

    Lazy load:
        .. code-block:: python

        docs = loader.load()
        print(docs)

        .. code-block:: python

        [Document(
            metadata={
                'request_id': 'xxxxxx-xxxx-xxxx-xxxx-xxxx',
                'generated_query': None,
                'screenshot': None},
            page_content="{
                'posts': [
                    {
                        'title': 'Launch Week Recap—make the web AI-ready', 
                        'url': 'https://www.agentql.com/blog/2024-launch-week-recap', 
                        'date': 'Nov 18, 2024', 
                        'author': 'Rachel-Lee Nabors'
                    }
                    ...
                ]
            }"
        ]
        
    """  # noqa: E501

    def __init__(
        self,
        url: str,
        query: str,
        api_key: Optional[str] = None,
        timeout: int = DEFAULT_API_TIMEOUT_SECONDS,
        is_stealth_mode_enabled: bool = DEFAULT_IS_STEALTH_MODE_ENABLED,
        wait_for: int = DEFAULT_WAIT_FOR_PAGE_LOAD_SECONDS,
        is_scroll_to_bottom_enabled: bool = DEFAULT_IS_SCROLL_TO_BOTTOM_ENABLED,
        mode: str = DEFAULT_RESPONSE_MODE,
        is_screenshot_enabled: bool = DEFAULT_IS_SCREENSHOT_ENABLED,
    ):
        """
        Initialize with API key and params.

        Args:
            url (str): The URL of the web page you want to extract data from.
            query (str): The AgentQL query to execute. Learn more at https://docs.agentql.com/agentql-query
            api_key (Optional[str]): AgentQL API key. You can create one at https://dev.agentql.com.
            timeout (int): Seconds to wait for a request. Defaults to 900.
            is_stealth_mode_enabled (boolean): Enable experimental anti-bot evasion strategies. May not work for all websites at all times. Defaults to `False`.
            wait_for (int): Wait time in seconds for page load (max 10 seconds). Defaults to 0.
            is_scroll_to_bottom_enabled (boolean): Whether to scroll to bottom of the page before extracting data. Defaults to `False`.
            mode (str): 'standard' uses deep data analysis, while 'fast' trades some depth of analysis for speed. Learn more at https://docs.agentql.com/accuracy/standard-mode. Defaults to 'fast'.
            is_screenshot_enabled (boolean): Whether to take a screenshot before extracting data. Returned in 'metadata' as a Base64 string. Defaults to `False`.

            Visit https://docs.agentql.com/rest-api/api-reference for more details.
        """
        self.url = url
        self.query = query

        self._api_key = api_key or os.getenv("AGENTQL_API_KEY")
        if not self._api_key:
            raise ValueError(UNSET_API_KEY_ERROR_MESSAGE)
        
        self.timeout = timeout

        self.params = {
            "wait_for": wait_for,
            "is_scroll_to_bottom_enabled": is_scroll_to_bottom_enabled,
            "mode": mode,
            "is_screenshot_enabled": is_screenshot_enabled,
        }

        self.metadata = {
            "experimental_stealth_mode_enabled": is_stealth_mode_enabled,
        }

    def lazy_load(self) -> Iterator[Document]:
        data = load_data(
            url=self.url,
            query=self.query,
            api_key=self._api_key,
            metadata=self.metadata,
            params=self.params,
            timeout=self.timeout,
        )
        yield Document(
            page_content=str(data["data"]),
            metadata=data["metadata"],
        )
