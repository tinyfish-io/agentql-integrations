from typing import Type

import pytest
from langchain_openai import ChatOpenAI
from langchain_tests.integration_tests import ToolsIntegrationTests

from langchain_agentql.tools import ExtractWebDataTool

from .test_data import TEST_DATA, TEST_QUERY, TEST_URL


class TestExtractWebDataToolIntegration(ToolsIntegrationTests):
    @property
    def tool_constructor(self) -> Type[ExtractWebDataTool]:
        return ExtractWebDataTool

    @property
    def tool_constructor_params(self) -> dict:
        # if your tool constructor instead required initialization arguments like
        # `def __init__(self, some_arg: int):`, you would return those here
        # as a dictionary, e.g.: `return {'some_arg': 42}`
        return {}

    @property
    def tool_invoke_params_example(self) -> dict:
        """
        Returns a dictionary representing the "args" of an example tool call.

        This should NOT be a ToolCall dict - i.e. it should not
        have {"name", "id", "args"} keys.
        """
        return {
            "url": TEST_URL,
            "query": TEST_QUERY,
            "prompt": None,
        }


class TestExtractWebDataToolCall:
    @pytest.fixture()
    def llm(self):
        tool = ExtractWebDataTool()
        llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
        )
        llm_with_tools = llm.bind_tools([tool])
        return llm_with_tools

    def test_extract_web_data_llm_tool_call(self, llm):
        msg = llm.invoke(
            f"Extract the data from {TEST_URL} using the following agentql query: {TEST_QUERY}"
        )
        tool_call_args_1 = {
            "url": TEST_URL,
            "query": TEST_QUERY,
            "prompt": None,
        }
        tool_call_args_2 = {
            "url": TEST_URL,
            "query": TEST_QUERY,
        }

        assert msg.tool_calls[0]["args"] in [tool_call_args_1, tool_call_args_2]

    async def test_extract_web_data_llm_tool_call_async(self, llm):
        msg = await llm.ainvoke(
            f"Extract the data from {TEST_URL} using the following agentql query: {TEST_QUERY}"
        )
        tool_call_args_1 = {
            "url": TEST_URL,
            "query": TEST_QUERY,
            "prompt": None,
        }
        tool_call_args_2 = {
            "url": TEST_URL,
            "query": TEST_QUERY,
        }

        assert msg.tool_calls[0]["args"] in [tool_call_args_1, tool_call_args_2]

    def test_extract_web_data_tool_invoke(self):
        tool = ExtractWebDataTool()
        res = tool.invoke(
            {
                "url": TEST_URL,
                "query": TEST_QUERY
            }
        )
        assert res["data"] == TEST_DATA


    async def test_extract_web_data_tool_invoke_async(self):
        tool = ExtractWebDataTool()
        res = await tool.ainvoke(
            {
                "url": TEST_URL,
                "query": TEST_QUERY
            }
        )

        assert res["data"] == TEST_DATA
