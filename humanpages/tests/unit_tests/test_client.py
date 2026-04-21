"""Unit tests for the HumanPagesClient."""

from unittest.mock import patch

import httpx
import pytest

from agentql_humanpages.client import HumanPagesClient
from agentql_humanpages.messages import (
    HUMANPAGES_UNAUTHORIZED_ERROR,
    UNSET_HUMANPAGES_API_KEY_ERROR,
)


def _mock_response(status_code: int, json_data: object, method: str = "GET", url: str = "https://humanpages.ai") -> httpx.Response:
    """Create a mock httpx.Response with a request attached."""
    request = httpx.Request(method, url)
    return httpx.Response(status_code, json=json_data, request=request)


class TestHumanPagesClientInit:
    def test_init_with_api_key(self) -> None:
        client = HumanPagesClient(api_key="test-key-123")
        assert client._api_key == "test-key-123"

    def test_init_from_env(self) -> None:
        with patch.dict("os.environ", {"HUMANPAGES_API_KEY": "env-key-456"}):
            client = HumanPagesClient()
            assert client._api_key == "env-key-456"

    def test_init_raises_without_key(self) -> None:
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError, match="No Human Pages API key"):
                HumanPagesClient()

    def test_init_custom_base_url(self) -> None:
        client = HumanPagesClient(api_key="k", base_url="https://custom.example.com/")
        assert client._base_url == "https://custom.example.com"


class TestHumanPagesClientSearchHumans:
    def test_search_humans_success(self) -> None:
        mock_humans = [{"id": "h1", "name": "Alice", "skills": ["web task"]}]
        resp = _mock_response(200, mock_humans)

        client = HumanPagesClient(api_key="test-key")
        with patch.object(httpx, "get", return_value=resp):
            result = client.search_humans(skill="web task")

        assert result == mock_humans

    def test_search_humans_unauthorized(self) -> None:
        resp = _mock_response(401, {"error": "unauthorized"})

        client = HumanPagesClient(api_key="bad-key")
        with patch.object(httpx, "get", side_effect=httpx.HTTPStatusError(
            "401", request=resp.request, response=resp
        )):
            with pytest.raises(ValueError, match="Invalid Human Pages API key"):
                client.search_humans()


class TestHumanPagesClientCreateJob:
    def test_create_job_success(self) -> None:
        mock_job = {"id": "job-1", "status": "pending"}
        resp = _mock_response(200, mock_job, method="POST")

        client = HumanPagesClient(api_key="test-key")
        with patch.object(httpx, "post", return_value=resp):
            result = client.create_job(
                human_id="h1",
                title="Extract data",
                description="Get product info from example.com",
            )

        assert result == mock_job

    def test_create_job_with_custom_params(self) -> None:
        mock_job = {"id": "job-2", "status": "pending"}
        resp = _mock_response(200, mock_job, method="POST")

        client = HumanPagesClient(api_key="test-key")
        with patch.object(httpx, "post", return_value=resp) as mock_post:
            client.create_job(
                human_id="h1",
                title="Extract data",
                description="Get data",
                price_usdc=10.0,
                deadline_hours=48,
            )

            call_kwargs = mock_post.call_args
            payload = call_kwargs.kwargs["json"]
            assert payload["priceUsdc"] == 10.0
            assert payload["deadlineHours"] == 48


class TestHumanPagesClientJobStatus:
    def test_get_job_status(self) -> None:
        mock_status = {"id": "job-1", "status": "completed"}
        resp = _mock_response(200, mock_status)

        client = HumanPagesClient(api_key="test-key")
        with patch.object(httpx, "get", return_value=resp):
            result = client.get_job_status("job-1")

        assert result["status"] == "completed"


class TestHumanPagesClientJobMessages:
    def test_get_job_messages(self) -> None:
        mock_messages = [{"id": "m1", "content": "Done!", "sender": "human"}]
        resp = _mock_response(200, mock_messages)

        client = HumanPagesClient(api_key="test-key")
        with patch.object(httpx, "get", return_value=resp):
            result = client.get_job_messages("job-1")

        assert len(result) == 1
        assert result[0]["content"] == "Done!"
