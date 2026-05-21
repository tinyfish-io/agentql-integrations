from importlib import metadata

from agentql_humanpages.agent import HumanFallbackAgent
from agentql_humanpages.client import HumanPagesClient
from agentql_humanpages.const import (
    DEFAULT_DEADLINE_HOURS,
    DEFAULT_POLL_INTERVAL_SECONDS,
    DEFAULT_PRICE_USDC,
    DEFAULT_TIMEOUT_SECONDS,
    HUMANPAGES_BASE_URL,
)

try:
    __version__ = metadata.version(__package__)
except metadata.PackageNotFoundError:
    # Case where package metadata is not available.
    __version__ = "0.1.0"

__all__ = [
    "DEFAULT_DEADLINE_HOURS",
    "DEFAULT_POLL_INTERVAL_SECONDS",
    "DEFAULT_PRICE_USDC",
    "DEFAULT_TIMEOUT_SECONDS",
    "HUMANPAGES_BASE_URL",
    "HumanFallbackAgent",
    "HumanPagesClient",
    "__version__",
]
