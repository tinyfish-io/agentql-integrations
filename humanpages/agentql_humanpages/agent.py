"""Human Fallback Agent -- uses AgentQL for web extraction with Human Pages fallback."""

import asyncio
import logging
import os
import time
from typing import Any, Optional

import httpx

from agentql_humanpages.client import HumanPagesClient
from agentql_humanpages.const import (
    AGENTQL_DEFAULT_MODE,
    AGENTQL_DEFAULT_TIMEOUT_SECONDS,
    AGENTQL_EXTRACT_DATA_ENDPOINT,
    DEFAULT_DEADLINE_HOURS,
    DEFAULT_MAX_POLL_ATTEMPTS,
    DEFAULT_POLL_INTERVAL_SECONDS,
    DEFAULT_PRICE_USDC,
    REQUEST_ORIGIN,
)
from agentql_humanpages.messages import (
    AGENTQL_EXTRACTION_FAILED,
    JOB_CREATION_FAILED_ERROR,
    JOB_TIMEOUT_ERROR,
    NO_HUMANS_AVAILABLE_ERROR,
    UNSET_AGENTQL_API_KEY_ERROR,
    UNSET_HUMANPAGES_API_KEY_ERROR,
)

logger = logging.getLogger(__name__)


class HumanFallbackAgent:
    """Agent that uses AgentQL for web data extraction with Human Pages as a fallback.

    When AgentQL extraction fails (network errors, anti-bot blocks, CAPTCHAs,
    or empty results), this agent automatically delegates the task to a human
    worker via the Human Pages platform.

    Setup:
        Set ``AGENTQL_API_KEY`` and ``HUMANPAGES_API_KEY`` environment variables,
        or pass them directly.

        .. code-block:: bash

            export AGENTQL_API_KEY="your-agentql-key"
            export HUMANPAGES_API_KEY="your-humanpages-key"

    Instantiation:
        .. code-block:: python

            from agentql_humanpages import HumanFallbackAgent

            agent = HumanFallbackAgent(
                agentql_api_key="your-agentql-key",
                humanpages_api_key="your-humanpages-key",
            )

    Usage:
        .. code-block:: python

            result = agent.extract(
                url="https://example.com/products",
                query="{ products[] { name price } }",
            )
    """

    def __init__(
        self,
        agentql_api_key: Optional[str] = None,
        humanpages_api_key: Optional[str] = None,
        agentql_timeout: int = AGENTQL_DEFAULT_TIMEOUT_SECONDS,
        agentql_mode: str = AGENTQL_DEFAULT_MODE,
        humanpages_base_url: Optional[str] = None,
        price_usdc: float = DEFAULT_PRICE_USDC,
        deadline_hours: int = DEFAULT_DEADLINE_HOURS,
        poll_interval: int = DEFAULT_POLL_INTERVAL_SECONDS,
        max_poll_attempts: int = DEFAULT_MAX_POLL_ATTEMPTS,
    ) -> None:
        """Initialize the Human Fallback Agent.

        Args:
            agentql_api_key: AgentQL API key. Falls back to AGENTQL_API_KEY env var.
            humanpages_api_key: Human Pages API key. Falls back to HUMANPAGES_API_KEY env var.
            agentql_timeout: Timeout in seconds for AgentQL requests.
            agentql_mode: AgentQL response mode ('fast' or 'standard').
            humanpages_base_url: Override the Human Pages base URL.
            price_usdc: Default price in USDC for human fallback jobs.
            deadline_hours: Default deadline in hours for human fallback jobs.
            poll_interval: Seconds between polling for job completion.
            max_poll_attempts: Maximum number of poll attempts before timing out.
        """
        self._agentql_api_key = agentql_api_key or os.getenv("AGENTQL_API_KEY")
        if not self._agentql_api_key:
            raise ValueError(UNSET_AGENTQL_API_KEY_ERROR)

        hp_api_key = humanpages_api_key or os.getenv("HUMANPAGES_API_KEY")
        if not hp_api_key:
            raise ValueError(UNSET_HUMANPAGES_API_KEY_ERROR)

        hp_kwargs: dict[str, Any] = {"api_key": hp_api_key}
        if humanpages_base_url:
            hp_kwargs["base_url"] = humanpages_base_url
        self._hp_client = HumanPagesClient(**hp_kwargs)

        self._agentql_timeout = agentql_timeout
        self._agentql_mode = agentql_mode
        self._price_usdc = price_usdc
        self._deadline_hours = deadline_hours
        self._poll_interval = poll_interval
        self._max_poll_attempts = max_poll_attempts

    def _agentql_extract(
        self,
        url: str,
        query: Optional[str] = None,
        prompt: Optional[str] = None,
    ) -> dict[str, Any]:
        """Attempt data extraction via the AgentQL REST API."""
        payload: dict[str, Any] = {
            "url": url,
            "query": query,
            "prompt": prompt,
            "params": {"mode": self._agentql_mode},
            "metadata": {},
        }
        headers = {
            "X-API-Key": self._agentql_api_key,
            "Content-Type": "application/json",
            "X-TF-Request-Origin": REQUEST_ORIGIN,
        }
        response = httpx.post(
            AGENTQL_EXTRACT_DATA_ENDPOINT,
            headers=headers,
            json=payload,
            timeout=self._agentql_timeout,
        )
        response.raise_for_status()
        return response.json()

    async def _agentql_extract_async(
        self,
        url: str,
        query: Optional[str] = None,
        prompt: Optional[str] = None,
    ) -> dict[str, Any]:
        """Async version of AgentQL extraction."""
        payload: dict[str, Any] = {
            "url": url,
            "query": query,
            "prompt": prompt,
            "params": {"mode": self._agentql_mode},
            "metadata": {},
        }
        headers = {
            "X-API-Key": self._agentql_api_key,
            "Content-Type": "application/json",
            "X-TF-Request-Origin": REQUEST_ORIGIN,
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(
                AGENTQL_EXTRACT_DATA_ENDPOINT,
                headers=headers,
                json=payload,
                timeout=self._agentql_timeout,
            )
            response.raise_for_status()
            return response.json()

    def _delegate_to_human(
        self,
        url: str,
        description: str,
        price_usdc: Optional[float] = None,
        deadline_hours: Optional[int] = None,
    ) -> dict[str, Any]:
        """Create a Human Pages job and poll until completion or timeout."""
        humans = self._hp_client.search_humans(skill="web task", available=True)
        if not humans:
            raise RuntimeError(NO_HUMANS_AVAILABLE_ERROR)

        human_id = humans[0]["id"]
        price = price_usdc if price_usdc is not None else self._price_usdc
        deadline = deadline_hours if deadline_hours is not None else self._deadline_hours

        try:
            job = self._hp_client.create_job(
                human_id=human_id,
                title=f"Extract data from {url}",
                description=description,
                price_usdc=price,
                deadline_hours=deadline,
            )
        except (ValueError, httpx.HTTPError) as e:
            raise RuntimeError(JOB_CREATION_FAILED_ERROR.format(detail=str(e))) from e

        job_id = job["id"]
        for _ in range(self._max_poll_attempts):
            status = self._hp_client.get_job_status(job_id)
            if status.get("status") == "completed":
                messages = self._hp_client.get_job_messages(job_id)
                return {
                    "source": "humanpages",
                    "job_id": job_id,
                    "status": status,
                    "messages": messages,
                }
            if status.get("status") in ("cancelled", "expired", "failed"):
                return {
                    "source": "humanpages",
                    "job_id": job_id,
                    "status": status,
                    "messages": [],
                }
            time.sleep(self._poll_interval)

        raise TimeoutError(JOB_TIMEOUT_ERROR.format(job_id=job_id))

    async def _adelegate_to_human(
        self,
        url: str,
        description: str,
        price_usdc: Optional[float] = None,
        deadline_hours: Optional[int] = None,
    ) -> dict[str, Any]:
        """Async version: create a Human Pages job and poll until completion or timeout."""
        humans = await self._hp_client.asearch_humans(skill="web task", available=True)
        if not humans:
            raise RuntimeError(NO_HUMANS_AVAILABLE_ERROR)

        human_id = humans[0]["id"]
        price = price_usdc if price_usdc is not None else self._price_usdc
        deadline = deadline_hours if deadline_hours is not None else self._deadline_hours

        try:
            job = await self._hp_client.acreate_job(
                human_id=human_id,
                title=f"Extract data from {url}",
                description=description,
                price_usdc=price,
                deadline_hours=deadline,
            )
        except (ValueError, httpx.HTTPError) as e:
            raise RuntimeError(JOB_CREATION_FAILED_ERROR.format(detail=str(e))) from e

        job_id = job["id"]
        for _ in range(self._max_poll_attempts):
            status = await self._hp_client.aget_job_status(job_id)
            if status.get("status") == "completed":
                messages = await self._hp_client.aget_job_messages(job_id)
                return {
                    "source": "humanpages",
                    "job_id": job_id,
                    "status": status,
                    "messages": messages,
                }
            if status.get("status") in ("cancelled", "expired", "failed"):
                return {
                    "source": "humanpages",
                    "job_id": job_id,
                    "status": status,
                    "messages": [],
                }
            await asyncio.sleep(self._poll_interval)

        raise TimeoutError(JOB_TIMEOUT_ERROR.format(job_id=job_id))

    def extract(
        self,
        url: str,
        query: Optional[str] = None,
        prompt: Optional[str] = None,
        fallback_description: Optional[str] = None,
        price_usdc: Optional[float] = None,
        deadline_hours: Optional[int] = None,
    ) -> dict[str, Any]:
        """Extract data from a URL using AgentQL, falling back to Human Pages on failure.

        First attempts extraction via the AgentQL REST API. If that fails for any
        reason (network error, anti-bot block, empty result), the task is delegated
        to a human worker on Human Pages.

        Args:
            url: The URL to extract data from.
            query: An AgentQL query string (mutually exclusive with prompt).
            prompt: A natural language description of the data to extract.
            fallback_description: Custom description for the human fallback job.
                If not provided, one is generated from the query/prompt.
            price_usdc: Override the default price for the human fallback job.
            deadline_hours: Override the default deadline for the human fallback job.

        Returns:
            A dict with keys:
                - ``source``: Either ``"agentql"`` or ``"humanpages"``.
                - ``data``: The extracted data (when source is agentql).
                - ``job_id``, ``status``, ``messages``: Job details (when source is humanpages).
        """
        if bool(query) == bool(prompt):
            raise ValueError("Exactly one of 'query' or 'prompt' must be provided.")

        # Attempt AgentQL extraction
        try:
            result = self._agentql_extract(url=url, query=query, prompt=prompt)
            data = result.get("data")
            if data:
                return {"source": "agentql", "data": data}
            logger.info("AgentQL returned empty data for %s, falling back to human.", url)
        except (httpx.HTTPError, httpx.TimeoutException, ValueError) as e:
            logger.info(
                AGENTQL_EXTRACTION_FAILED.format(url=url, detail=str(e))
            )

        # Build fallback description
        if not fallback_description:
            task_detail = query if query else prompt
            fallback_description = (
                f"Please visit {url} and extract the following data:\n\n{task_detail}\n\n"
                f"Return the results as structured JSON."
            )

        return self._delegate_to_human(
            url=url,
            description=fallback_description,
            price_usdc=price_usdc,
            deadline_hours=deadline_hours,
        )

    async def aextract(
        self,
        url: str,
        query: Optional[str] = None,
        prompt: Optional[str] = None,
        fallback_description: Optional[str] = None,
        price_usdc: Optional[float] = None,
        deadline_hours: Optional[int] = None,
    ) -> dict[str, Any]:
        """Async version of extract. See extract() for full documentation."""
        if bool(query) == bool(prompt):
            raise ValueError("Exactly one of 'query' or 'prompt' must be provided.")

        try:
            result = await self._agentql_extract_async(url=url, query=query, prompt=prompt)
            data = result.get("data")
            if data:
                return {"source": "agentql", "data": data}
            logger.info("AgentQL returned empty data for %s, falling back to human.", url)
        except (httpx.HTTPError, httpx.TimeoutException, ValueError) as e:
            logger.info(
                AGENTQL_EXTRACTION_FAILED.format(url=url, detail=str(e))
            )

        if not fallback_description:
            task_detail = query if query else prompt
            fallback_description = (
                f"Please visit {url} and extract the following data:\n\n{task_detail}\n\n"
                f"Return the results as structured JSON."
            )

        return await self._adelegate_to_human(
            url=url,
            description=fallback_description,
            price_usdc=price_usdc,
            deadline_hours=deadline_hours,
        )
