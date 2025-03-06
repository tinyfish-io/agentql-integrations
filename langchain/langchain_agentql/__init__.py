from importlib import metadata

from langchain_agentql.document_loaders import AgentQLLoader
from langchain_agentql.toolkits import AgentQLBrowserToolkit
from langchain_agentql.tools import (
    ExtractWebDataBrowserTool,
    ExtractWebDataTool,
    GetWebElementBrowserTool,
)

try:
    __version__ = metadata.version(__package__)
except metadata.PackageNotFoundError:
    # Case where package metadata is not available.
    __version__ = "1.0.0"

__all__ = [
    "AgentQLBrowserToolkit",
    "AgentQLLoader",
    "ExtractWebDataBrowserTool",
    "ExtractWebDataTool",
    "GetWebElementBrowserTool",
    "__version__",
]
