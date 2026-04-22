"""Unit tests for the HumanFallbackAgent."""

from unittest.mock import patch

import httpx
import pytest

from agentql_humanpages.agent import HumanFallbackAgent


def _mock_response(status_code: int, json_data: object, method: str = "POST", url: str = "https://api.agentql.com/v1/query-data") -> httpx.Response:
    """Create a mock httpx.Response with a request attached."""
    request = httpx.Request(method, url)
    return httpx.Response(status_code, json=json_data, request=request)


@pytest.fixture()
def agent() -> HumanFallbackAgent:
    """Create an agent with test keys."""
    return HumanFallbackAgent(
        agentql_api_key="test-agentql-key",
        humanpages_api_key="test-hp-key",
        poll_interval=0,  # No waiting in tests
        max_poll_attempts=2,
    )


class TestHumanFallbackAgentInit:
    def test_init_with_keys(self) -> None:
        agent = HumanFallbackAgent(
            agentql_api_key="aql-key",
            humanpages_api_key="hp-key",
        )
        assert agent._agentql_api_key == "aql-key"

    def test_init_from_env(self) -> None:
        with patch.dict("os.environ", {
            "AGENTQL_API_KEY": "env-aql",
            "HUMANPAGES_API_KEY": "env-hp",
        }):
            agent = HumanFallbackAgent()
            assert agent._agentql_api_key == "env-aql"

    def test_init_raises_without_agentql_key(self) -> None:
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError, match="No AgentQL API key"):
                HumanFallbackAgent(humanpages_api_key="hp-key")

    def test_init_raises_without_humanpages_key(self) -> None:
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError, match="No Human Pages API key"):
                HumanFallbackAgent(agentql_api_key="aql-key")


class TestExtractWithAgentQL:
    def test_extract_success_via_agentql(self, agent: HumanFallbackAgent) -> None:
        agentql_response = {
            "data": {"products": [{"name": "Widget", "price": 9.99}]},
            "metadata": {"request_id": "abc123"},
        }
        resp = _mock_response(200, agentql_response)

        with patch.object(httpx, "post", return_value=resp):
            result = agent.extract(
                url="https://example.com/products",
                query="{ products[] { name price } }",
            )

        assert result["source"] == "agentql"
        assert result["data"]["products"][0]["name"] == "Widget"

    def test_extract_requires_query_or_prompt(self, agent: HumanFallbackAgent) -> None:
        with pytest.raises(ValueError, match="Either 'query' or 'prompt'"):
            agent.extract(url="https://example.com")


class TestFallbackToHuman:
    def test_fallback_on_agentql_http_error(self, agent: HumanFallbackAgent) -> None:
        """When AgentQL returns an error, the agent falls back to Human Pages."""
        agentql_error = _mock_response(500, {"error": "Internal Server Error"})

        mock_humans = [{"id": "h1", "name": "Alice"}]
        mock_job = {"id": "job-1", "status": "pending"}
        mock_status = {"id": "job-1", "status": "completed"}
        mock_messages = [{"content": '{"products": [{"name": "Widget"}]}'}]

        hp_client = agent._hp_client
        with (
            patch.object(
                httpx, "post",
                side_effect=httpx.HTTPStatusError(
                    "500", request=agentql_error.request, response=agentql_error
                ),
            ),
            patch.object(hp_client, "search_humans", return_value=mock_humans),
            patch.object(hp_client, "create_job", return_value=mock_job),
            patch.object(hp_client, "get_job_status", return_value=mock_status),
            patch.object(hp_client, "get_job_messages", return_value=mock_messages),
        ):
            result = agent.extract(
                url="https://example.com",
                query="{ products[] { name } }",
            )

        assert result["source"] == "humanpages"
        assert result["job_id"] == "job-1"
        assert len(result["messages"]) == 1

    def test_fallback_on_agentql_empty_data(self, agent: HumanFallbackAgent) -> None:
        """When AgentQL returns empty data, the agent falls back to Human Pages."""
        resp = _mock_response(200, {"data": None, "metadata": {}})

        mock_humans = [{"id": "h1", "name": "Bob"}]
        mock_job = {"id": "job-2", "status": "pending"}
        mock_status = {"id": "job-2", "status": "completed"}
        mock_messages = [{"content": "result data"}]

        hp_client = agent._hp_client
        with (
            patch.object(httpx, "post", return_value=resp),
            patch.object(hp_client, "search_humans", return_value=mock_humans),
            patch.object(hp_client, "create_job", return_value=mock_job),
            patch.object(hp_client, "get_job_status", return_value=mock_status),
            patch.object(hp_client, "get_job_messages", return_value=mock_messages),
        ):
            result = agent.extract(
                url="https://example.com",
                prompt="Get all product names",
            )

        assert result["source"] == "humanpages"

    def test_fallback_no_humans_available(self, agent: HumanFallbackAgent) -> None:
        """When no humans are available, a RuntimeError is raised."""
        resp = _mock_response(200, {"data": None, "metadata": {}})

        hp_client = agent._hp_client
        with (
            patch.object(httpx, "post", return_value=resp),
            patch.object(hp_client, "search_humans", return_value=[]),
        ):
            with pytest.raises(RuntimeError, match="No humans are currently available"):
                agent.extract(
                    url="https://example.com",
                    query="{ data }",
                )

    def test_fallback_job_timeout(self, agent: HumanFallbackAgent) -> None:
        """When the job does not complete in time, a TimeoutError is raised."""
        resp = _mock_response(200, {"data": None, "metadata": {}})

        mock_humans = [{"id": "h1", "name": "Carol"}]
        mock_job = {"id": "job-3", "status": "pending"}
        mock_status = {"id": "job-3", "status": "in_progress"}

        hp_client = agent._hp_client
        with (
            patch.object(httpx, "post", return_value=resp),
            patch.object(hp_client, "search_humans", return_value=mock_humans),
            patch.object(hp_client, "create_job", return_value=mock_job),
            patch.object(hp_client, "get_job_status", return_value=mock_status),
        ):
            with pytest.raises(TimeoutError, match="did not complete"):
                agent.extract(
                    url="https://example.com",
                    query="{ data }",
                )

    def test_fallback_cancelled_job(self, agent: HumanFallbackAgent) -> None:
        """When a job is cancelled, results are returned with empty messages."""
        resp = _mock_response(200, {"data": None, "metadata": {}})

        mock_humans = [{"id": "h1", "name": "Dave"}]
        mock_job = {"id": "job-4", "status": "pending"}
        mock_status = {"id": "job-4", "status": "cancelled"}

        hp_client = agent._hp_client
        with (
            patch.object(httpx, "post", return_value=resp),
            patch.object(hp_client, "search_humans", return_value=mock_humans),
            patch.object(hp_client, "create_job", return_value=mock_job),
            patch.object(hp_client, "get_job_status", return_value=mock_status),
        ):
            result = agent.extract(
                url="https://example.com",
                query="{ data }",
            )

        assert result["source"] == "humanpages"
        assert result["status"]["status"] == "cancelled"
        assert result["messages"] == []
