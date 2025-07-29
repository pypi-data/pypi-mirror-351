from importlib.metadata import version
from typing import Optional

from restructured._generated.openapi_client import ApiClient  # type: ignore
from restructured._generated.openapi_client import Configuration  # type: ignore
from restructured._resources.agent_run import AgentRun
from restructured._utils.config import get_api_key
from restructured._utils.config import get_host

RESTRUCTURED_VERSION = version("restructured")


def _get_client(
    api_key: Optional[str] = None,
    host: Optional[str] = None,
) -> ApiClient:
    if api_key is None:
        api_key = get_api_key()
    if host is None:
        host = get_host()

    if api_key is None:
        raise ValueError("No API token provided")

    configuration = Configuration(
        host=host,
        access_token=api_key,
    )
    client = ApiClient(configuration)
    client.user_agent = f"restructured-python-{RESTRUCTURED_VERSION}"
    return client


class Restructured:
    """Main client class for interacting with the Restructured API."""

    agent_run: AgentRun

    def __init__(
        self,
        api_key: Optional[str] = None,
        host: Optional[str] = None,
    ) -> None:
        """Initialize the Restructured client.

        Args:
            api_key: Optional API key. If not provided, will attempt to load from environment.
            host: Optional API host. If not provided, will use default host.
        """
        self._client = _get_client(api_key=api_key, host=host)
        self.agent_run = AgentRun(self._client)
