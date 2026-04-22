"""Human Pages REST API client."""

import os
from typing import Any, Optional
from urllib.parse import quote

import httpx

from agentql_humanpages.const import (
    CREATE_JOB_ENDPOINT,
    DEFAULT_DEADLINE_HOURS,
    DEFAULT_PRICE_USDC,
    DEFAULT_TIMEOUT_SECONDS,
    HUMANPAGES_BASE_URL,
    JOB_MESSAGES_ENDPOINT,
    JOB_STATUS_ENDPOINT,
    SEARCH_HUMANS_ENDPOINT,
)
from agentql_humanpages.messages import (
    HUMANPAGES_UNAUTHORIZED_ERROR,
    UNSET_HUMANPAGES_API_KEY_ERROR,
)


class HumanPagesClient:
    """Client for the Human Pages REST API.

    Provides methods to search for available humans, create jobs,
    check job status, and retrieve job messages.

    Setup:
        Set the ``HUMANPAGES_API_KEY`` environment variable or pass the key directly.

        .. code-block:: bash

            export HUMANPAGES_API_KEY="your-api-key"

    Instantiation:
        .. code-block:: python

            client = HumanPagesClient()
            # or
            client = HumanPagesClient(api_key="your-api-key")
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = HUMANPAGES_BASE_URL,
        timeout: int = DEFAULT_TIMEOUT_SECONDS,
    ) -> None:
        self._api_key = api_key or os.getenv("HUMANPAGES_API_KEY")
        if not self._api_key:
            raise ValueError(UNSET_HUMANPAGES_API_KEY_ERROR)
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

    def _headers(self) -> dict[str, str]:
        return {
            "Content-Type": "application/json",
            "X-Agent-Key": self._api_key,
        }

    def _handle_error(self, e: httpx.HTTPStatusError) -> None:
        if e.response.status_code == httpx.codes.UNAUTHORIZED:
            raise ValueError(HUMANPAGES_UNAUTHORIZED_ERROR) from e
        msg = e.response.text
        try:
            error_json = e.response.json()
            if isinstance(error_json, dict):
                msg = error_json.get("error", error_json.get("message", str(error_json)))
            else:
                msg = str(error_json)
        except (ValueError, TypeError):
            msg = f"HTTP {e}"
        raise ValueError(msg) from e

    def search_humans(
        self,
        skill: str = "web task",
        available: bool = True,
    ) -> list[dict[str, Any]]:
        """Search for available humans with a given skill.

        Args:
            skill: The skill to search for (default: "web task").
            available: Whether to filter for available humans only.

        Returns:
            A list of human profiles matching the search criteria.
        """
        params = {"skill": skill, "available": str(available).lower()}
        try:
            response = httpx.get(
                f"{self._base_url}{SEARCH_HUMANS_ENDPOINT}",
                params=params,
                headers=self._headers(),
                timeout=self._timeout,
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            self._handle_error(e)
        return response.json()

    def create_job(
        self,
        human_id: str,
        title: str,
        description: str,
        price_usdc: float = DEFAULT_PRICE_USDC,
        deadline_hours: int = DEFAULT_DEADLINE_HOURS,
    ) -> dict[str, Any]:
        """Create a new job for a human to complete.

        Args:
            human_id: The ID of the human to assign the job to.
            title: A short title for the job.
            description: A detailed description of what needs to be done.
            price_usdc: The price in USDC to pay for the job.
            deadline_hours: The number of hours to complete the job.

        Returns:
            The created job object including its ID and status.
        """
        payload = {
            "humanId": human_id,
            "title": title,
            "description": description,
            "priceUsdc": price_usdc,
            "deadlineHours": deadline_hours,
        }
        try:
            response = httpx.post(
                f"{self._base_url}{CREATE_JOB_ENDPOINT}",
                json=payload,
                headers=self._headers(),
                timeout=self._timeout,
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            self._handle_error(e)
        return response.json()

    def get_job_status(self, job_id: str) -> dict[str, Any]:
        """Check the status of a job.

        Args:
            job_id: The ID of the job to check.

        Returns:
            The job object with its current status.
        """
        url = f"{self._base_url}{JOB_STATUS_ENDPOINT.format(job_id=quote(job_id, safe=''))}"
        try:
            response = httpx.get(
                url,
                headers=self._headers(),
                timeout=self._timeout,
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            self._handle_error(e)
        return response.json()

    def get_job_messages(self, job_id: str) -> list[dict[str, Any]]:
        """Retrieve messages exchanged on a job.

        Args:
            job_id: The ID of the job.

        Returns:
            A list of message objects for the job.
        """
        url = f"{self._base_url}{JOB_MESSAGES_ENDPOINT.format(job_id=quote(job_id, safe=''))}"
        try:
            response = httpx.get(
                url,
                headers=self._headers(),
                timeout=self._timeout,
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            self._handle_error(e)
        return response.json()

    async def asearch_humans(
        self,
        skill: str = "web task",
        available: bool = True,
    ) -> list[dict[str, Any]]:
        """Async version of search_humans."""
        params = {"skill": skill, "available": str(available).lower()}
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self._base_url}{SEARCH_HUMANS_ENDPOINT}",
                    params=params,
                    headers=self._headers(),
                    timeout=self._timeout,
                )
                response.raise_for_status()
            except httpx.HTTPStatusError as e:
                self._handle_error(e)
        return response.json()

    async def acreate_job(
        self,
        human_id: str,
        title: str,
        description: str,
        price_usdc: float = DEFAULT_PRICE_USDC,
        deadline_hours: int = DEFAULT_DEADLINE_HOURS,
    ) -> dict[str, Any]:
        """Async version of create_job."""
        payload = {
            "humanId": human_id,
            "title": title,
            "description": description,
            "priceUsdc": price_usdc,
            "deadlineHours": deadline_hours,
        }
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self._base_url}{CREATE_JOB_ENDPOINT}",
                    json=payload,
                    headers=self._headers(),
                    timeout=self._timeout,
                )
                response.raise_for_status()
            except httpx.HTTPStatusError as e:
                self._handle_error(e)
        return response.json()

    async def aget_job_status(self, job_id: str) -> dict[str, Any]:
        """Async version of get_job_status."""
        url = f"{self._base_url}{JOB_STATUS_ENDPOINT.format(job_id=quote(job_id, safe=''))}"
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    url,
                    headers=self._headers(),
                    timeout=self._timeout,
                )
                response.raise_for_status()
            except httpx.HTTPStatusError as e:
                self._handle_error(e)
        return response.json()

    async def aget_job_messages(self, job_id: str) -> list[dict[str, Any]]:
        """Async version of get_job_messages."""
        url = f"{self._base_url}{JOB_MESSAGES_ENDPOINT.format(job_id=quote(job_id, safe=''))}"
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    url,
                    headers=self._headers(),
                    timeout=self._timeout,
                )
                response.raise_for_status()
            except httpx.HTTPStatusError as e:
                self._handle_error(e)
        return response.json()
