from typing import List

from flyte.remote._client.auth import AuthType, ClientConfig

from ._controller import RemoteController

__all__ = ["RemoteController", "create_remote_controller"]


def create_remote_controller(
    *,
    api_key: str | None = None,
    auth_type: AuthType = "Pkce",
    endpoint: str,
    client_config: ClientConfig | None = None,
    headless: bool = False,
    insecure: bool = False,
    insecure_skip_verify: bool = False,
    ca_cert_file_path: str | None = None,
    command: List[str] | None = None,
    proxy_command: List[str] | None = None,
    client_id: str | None = None,
    client_credentials_secret: str | None = None,
    rpc_retries: int = 3,
    http_proxy_url: str | None = None,
) -> RemoteController:
    """
    Create a new instance of the remote controller.
    """
    from ._client import ControllerClient
    from ._controller import RemoteController

    controller = RemoteController(
        client_coro=ControllerClient.for_endpoint(
            endpoint=endpoint, insecure=insecure, insecure_skip_verify=insecure_skip_verify
        ),
        workers=10,
        max_system_retries=5,
    )
    return controller
