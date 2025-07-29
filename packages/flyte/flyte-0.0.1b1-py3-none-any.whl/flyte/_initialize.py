from __future__ import annotations

import datetime
import functools
import os
import threading
import typing
from dataclasses import dataclass, replace
from datetime import timedelta
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, ClassVar, Dict, List, Literal, Optional, TypeVar

from flyte.errors import InitializationError

from ._api_commons import syncer
from ._logging import initialize_logger
from ._tools import ipython_check

if TYPE_CHECKING:
    from flyte.config import Config
    from flyte.remote._client.auth import AuthType, ClientConfig
    from flyte.remote._client.controlplane import ClientSet

Mode = Literal["local", "remote"]


def set_if_exists(d: dict, k: str, val: typing.Any) -> dict:
    """
    Given a dict ``d`` sets the key ``k`` with value of config ``v``, if the config value ``v`` is set
    and return the updated dictionary.
    """
    exists = isinstance(val, bool) or bool(val is not None and val)
    if exists:
        d[k] = val
    return d


@dataclass(init=True, repr=True, eq=True, frozen=True)
class Storage(object):
    """
    Data storage configuration that applies across any provider.
    """

    retries: int = 3
    backoff: datetime.timedelta = datetime.timedelta(seconds=5)
    enable_debug: bool = False
    attach_execution_metadata: bool = True

    _KEY_ENV_VAR_MAPPING: ClassVar[typing.Dict[str, str]] = {
        "enable_debug": "UNION_STORAGE_DEBUG",
        "retries": "UNION_STORAGE_RETRIES",
        "backoff": "UNION_STORAGE_BACKOFF_SECONDS",
    }

    def get_fsspec_kwargs(self, anonymous: bool = False, /, **kwargs) -> Dict[str, Any]:
        """
        Returns the configuration as kwargs for constructing an fsspec filesystem.
        """
        return {}

    @classmethod
    def _auto_as_kwargs(cls) -> Dict[str, Any]:
        retries = os.getenv(cls._KEY_ENV_VAR_MAPPING["retries"])
        backoff = os.getenv(cls._KEY_ENV_VAR_MAPPING["backoff"])
        enable_debug = os.getenv(cls._KEY_ENV_VAR_MAPPING["enable_debug"])

        kwargs: Dict[str, Any] = {}
        kwargs = set_if_exists(kwargs, "enable_debug", enable_debug)
        kwargs = set_if_exists(kwargs, "retries", retries)
        kwargs = set_if_exists(kwargs, "backoff", backoff)
        return kwargs

    @classmethod
    def auto(cls) -> Storage:
        """
        Construct the config object automatically from environment variables.
        """
        return cls(**cls._auto_as_kwargs())


@dataclass(init=True, repr=True, eq=True, frozen=True)
class S3(Storage):
    """
    S3 specific configuration
    """

    endpoint: typing.Optional[str] = None
    access_key_id: typing.Optional[str] = None
    secret_access_key: typing.Optional[str] = None

    _KEY_ENV_VAR_MAPPING: ClassVar[typing.Dict[str, str]] = {
        "endpoint": "FLYTE_AWS_ENDPOINT",
        "access_key_id": "FLYTE_AWS_ACCESS_KEY_ID",
        "secret_access_key": "FLYTE_AWS_SECRET_ACCESS_KEY",
    } | Storage._KEY_ENV_VAR_MAPPING

    # Refer to https://github.com/developmentseed/obstore/blob/33654fc37f19a657689eb93327b621e9f9e01494/obstore/python/obstore/store/_aws.pyi#L11
    # for key and secret
    _CONFIG_KEY_FSSPEC_S3_KEY_ID: ClassVar = "access_key_id"
    _CONFIG_KEY_FSSPEC_S3_SECRET: ClassVar = "secret_access_key"
    _CONFIG_KEY_ENDPOINT: ClassVar = "endpoint_url"
    _KEY_SKIP_SIGNATURE: ClassVar = "skip_signature"

    @classmethod
    def auto(cls) -> S3:
        """
        :return: Config
        """
        endpoint = os.getenv(cls._KEY_ENV_VAR_MAPPING["endpoint"], None)
        access_key_id = os.getenv(cls._KEY_ENV_VAR_MAPPING["access_key_id"], None)
        secret_access_key = os.getenv(cls._KEY_ENV_VAR_MAPPING["secret_access_key"], None)

        kwargs = super()._auto_as_kwargs()
        kwargs = set_if_exists(kwargs, "endpoint", endpoint)
        kwargs = set_if_exists(kwargs, "access_key_id", access_key_id)
        kwargs = set_if_exists(kwargs, "secret_access_key", secret_access_key)

        return S3(**kwargs)

    @classmethod
    def for_sandbox(cls) -> S3:
        """
        :return:
        """
        kwargs = super()._auto_as_kwargs()
        final_kwargs = kwargs | {
            "endpoint": "http://localhost:4566",
            "access_key_id": "minio",
            "secret_access_key": "miniostorage",
        }
        return S3(**final_kwargs)

    def get_fsspec_kwargs(self, anonymous: bool = False, /, **kwargs) -> Dict[str, Any]:
        # Construct the config object
        config: Dict[str, Any] = {}
        if self._CONFIG_KEY_FSSPEC_S3_KEY_ID in kwargs or self.access_key_id:
            config[self._CONFIG_KEY_FSSPEC_S3_KEY_ID] = kwargs.pop(
                self._CONFIG_KEY_FSSPEC_S3_KEY_ID, self.access_key_id
            )
        if self._CONFIG_KEY_FSSPEC_S3_SECRET in kwargs or self.secret_access_key:
            config[self._CONFIG_KEY_FSSPEC_S3_SECRET] = kwargs.pop(
                self._CONFIG_KEY_FSSPEC_S3_SECRET, self.secret_access_key
            )
        if self._CONFIG_KEY_ENDPOINT in kwargs or self.endpoint:
            config["endpoint_url"] = kwargs.pop(self._CONFIG_KEY_ENDPOINT, self.endpoint)

        retries = kwargs.pop("retries", self.retries)
        backoff = kwargs.pop("backoff", self.backoff)

        if anonymous:
            config[self._KEY_SKIP_SIGNATURE] = True

        retry_config = {
            "max_retries": retries,
            "backoff": {
                "base": 2,
                "init_backoff": backoff,
                "max_backoff": timedelta(seconds=16),
            },
            "retry_timeout": timedelta(minutes=3),
        }

        client_options = {"timeout": "99999s", "allow_http": True}

        if config:
            kwargs["config"] = config
        kwargs["client_options"] = client_options or None
        kwargs["retry_config"] = retry_config or None

        return kwargs


@dataclass(init=True, repr=True, eq=True, frozen=True)
class GCS(Storage):
    """
    Any GCS specific configuration.
    """

    gsutil_parallelism: bool = False

    _KEY_ENV_VAR_MAPPING: ClassVar[dict[str, str]] = {
        "gsutil_parallelism": "GCP_GSUTIL_PARALLELISM",
    }

    @classmethod
    def auto(cls) -> GCS:
        gsutil_parallelism = os.getenv(cls._KEY_ENV_VAR_MAPPING["gsutil_parallelism"], None)

        kwargs: Dict[str, Any] = {}
        kwargs = set_if_exists(kwargs, "gsutil_parallelism", gsutil_parallelism)
        return GCS(**kwargs)

    def get_fsspec_kwargs(self, anonymous: bool = False, /, **kwargs) -> Dict[str, Any]:
        return kwargs


@dataclass(init=True, repr=True, eq=True, frozen=True)
class ABFS(Storage):
    """
    Any Azure Blob Storage specific configuration.
    """

    account_name: typing.Optional[str] = None
    account_key: typing.Optional[str] = None
    tenant_id: typing.Optional[str] = None
    client_id: typing.Optional[str] = None
    client_secret: typing.Optional[str] = None

    _KEY_ENV_VAR_MAPPING: ClassVar[dict[str, str]] = {
        "account_name": "AZURE_STORAGE_ACCOUNT_NAME",
        "account_key": "AZURE_STORAGE_ACCOUNT_KEY",
        "tenant_id": "AZURE_TENANT_ID",
        "client_id": "AZURE_CLIENT_ID",
        "client_secret": "AZURE_CLIENT_SECRET",
    }
    _KEY_SKIP_SIGNATURE: ClassVar = "skip_signature"

    @classmethod
    def auto(cls) -> ABFS:
        account_name = os.getenv(cls._KEY_ENV_VAR_MAPPING["account_name"], None)
        account_key = os.getenv(cls._KEY_ENV_VAR_MAPPING["account_key"], None)
        tenant_id = os.getenv(cls._KEY_ENV_VAR_MAPPING["tenant_id"], None)
        client_id = os.getenv(cls._KEY_ENV_VAR_MAPPING["client_id"], None)
        client_secret = os.getenv(cls._KEY_ENV_VAR_MAPPING["client_secret"], None)

        kwargs: Dict[str, Any] = {}
        kwargs = set_if_exists(kwargs, "account_name", account_name)
        kwargs = set_if_exists(kwargs, "account_key", account_key)
        kwargs = set_if_exists(kwargs, "tenant_id", tenant_id)
        kwargs = set_if_exists(kwargs, "client_id", client_id)
        kwargs = set_if_exists(kwargs, "client_secret", client_secret)
        return ABFS(**kwargs)

    def get_fsspec_kwargs(self, anonymous: bool = False, /, **kwargs) -> Dict[str, Any]:
        config: Dict[str, Any] = {}
        if "account_name" in kwargs or self.account_name:
            config["account_name"] = kwargs.get("account_name", self.account_name)
        if "account_key" in kwargs or self.account_key:
            config["account_key"] = kwargs.get("account_key", self.account_key)
        if "client_id" in kwargs or self.client_id:
            config["client_id"] = kwargs.get("client_id", self.client_id)
        if "client_secret" in kwargs or self.client_secret:
            config["client_secret"] = kwargs.get("client_secret", self.client_secret)
        if "tenant_id" in kwargs or self.tenant_id:
            config["tenant_id"] = kwargs.get("tenant_id", self.tenant_id)

        if anonymous:
            config[self._KEY_SKIP_SIGNATURE] = True

        client_options = {"timeout": "99999s", "allow_http": "true"}

        if config:
            kwargs["config"] = config
        kwargs["client_options"] = client_options

        return kwargs


@dataclass(init=True, repr=True, eq=True, frozen=True, kw_only=True)
class CommonInit:
    """
    Common initialization configuration for Flyte.
    """

    root_dir: Path
    org: str | None = None
    project: str | None = None
    domain: str | None = None


@dataclass(init=True, kw_only=True, repr=True, eq=True, frozen=True)
class _InitConfig(CommonInit):
    client: Optional[ClientSet] = None
    storage: Optional[Storage] = None

    def replace(self, **kwargs) -> _InitConfig:
        return replace(self, **kwargs)


# Global singleton to store initialization configuration
_init_config: _InitConfig | None = None
_init_lock = threading.RLock()  # Reentrant lock for thread safety


async def _initialize_client(
    api_key: str | None = None,
    auth_type: AuthType = "Pkce",
    endpoint: str | None = None,
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
) -> ClientSet:
    """
    Initialize the client based on the execution mode.
    :return: The initialized client
    """
    from flyte.remote._client.controlplane import ClientSet

    if endpoint is not None:
        return await ClientSet.for_endpoint(
            endpoint,
            insecure=insecure,
            api_key=api_key,
            insecure_skip_verify=insecure_skip_verify,
            auth_type=auth_type,
            headless=headless,
            ca_cert_file_path=ca_cert_file_path,
            command=command,
            proxy_command=proxy_command,
            client_id=client_id,
            client_credentials_secret=client_credentials_secret,
            client_config=client_config,
            rpc_retries=rpc_retries,
            http_proxy_url=http_proxy_url,
        )
    raise NotImplementedError("Currently only endpoints are supported.")


@syncer.wrap
async def init(
    org: str | None = None,
    project: str | None = None,
    domain: str | None = None,
    root_dir: Path | None = None,
    log_level: int | None = None,
    endpoint: str | None = None,
    headless: bool = False,
    insecure: bool = False,
    insecure_skip_verify: bool = False,
    ca_cert_file_path: str | None = None,
    auth_type: AuthType = "Pkce",
    command: List[str] | None = None,
    proxy_command: List[str] | None = None,
    api_key: str | None = None,
    client_id: str | None = None,
    client_credentials_secret: str | None = None,
    auth_client_config: ClientConfig | None = None,
    rpc_retries: int = 3,
    http_proxy_url: str | None = None,
    storage: Storage | None = None,
    config: Config | None = None,
) -> None:
    """
    Initialize the Flyte system with the given configuration. This method should be called before any other Flyte
    remote API methods are called. Thread-safe implementation.

    :param project: Optional project name (not used in this implementation)
    :param domain: Optional domain name (not used in this implementation)
    :param root_dir: Optional root directory from which to determine how to load files, and find paths to files.
      defaults to the editable install directory if the cwd is in a Python editable install, else just the cwd.
    :param log_level: Optional logging level for the logger, default is set using the default initialization policies
    :param api_key: Optional API key for authentication
    :param endpoint: Optional API endpoint URL
    :param headless: Optional Whether to run in headless mode
    :param mode: Optional execution model (local, remote). Default is local. When local is used,
           the execution will be done locally. When remote is used, the execution will be sent to a remote server,
           In the remote case, the endpoint or api_key must be set.
    :param insecure_skip_verify: Whether to skip SSL certificate verification
    :param auth_client_config: Optional client configuration for authentication
    :param auth_type: The authentication type to use (Pkce, ClientSecret, ExternalCommand, DeviceFlow)
    :param command: This command is executed to return a token using an external process
    :param proxy_command: This command is executed to return a token for proxy authorization using an external process
    :param client_id: This is the public identifier for the app which handles authorization for a Flyte deployment.
      More details here: https://www.oauth.com/oauth2-servers/client-registration/client-id-secret/.
    :param client_credentials_secret: Used for service auth, which is automatically called during pyflyte. This will
      allow the Flyte engine to read the password directly from the environment variable. Note that this is
      less secure! Please only use this if mounting the secret as a file is impossible
    :param ca_cert_file_path: [optional] str Root Cert to be loaded and used to verify admin
    :param http_proxy_url: [optional] HTTP Proxy to be used for OAuth requests
    :param rpc_retries: [optional] int Number of times to retry the platform calls
    :param audience: oauth2 audience for the token request. This is used to validate the token
    :param insecure: insecure flag for the client
    :param storage: Optional blob store (S3, GCS, Azure) configuration if needed to access (i.e. using Minio)
    :param org: Optional organization override for the client. Should be set by auth instead.
    :param config: Optional config to override the init parameters

    :return: None
    """
    from flyte._utils import get_cwd_editable_install

    interactive_mode = ipython_check()

    initialize_logger(enable_rich=interactive_mode)
    if log_level:
        initialize_logger(log_level=log_level, enable_rich=interactive_mode)

    global _init_config  # noqa: PLW0603

    with _init_lock:
        if config is None:
            from flyte.config import Config

            config = Config.auto()
        platform_cfg = config.platform
        task_cfg = config.task
        client = None
        if endpoint or platform_cfg.endpoint or api_key:
            client = await _initialize_client(
                api_key=api_key,
                auth_type=auth_type or platform_cfg.auth_mode,
                endpoint=endpoint or platform_cfg.endpoint,
                headless=headless,
                insecure=insecure or platform_cfg.insecure,
                insecure_skip_verify=insecure_skip_verify or platform_cfg.insecure_skip_verify,
                ca_cert_file_path=ca_cert_file_path or platform_cfg.ca_cert_file_path,
                command=command or platform_cfg.command,
                proxy_command=proxy_command or platform_cfg.proxy_command,
                client_id=client_id or platform_cfg.client_id,
                client_credentials_secret=client_credentials_secret or platform_cfg.client_credentials_secret,
                client_config=auth_client_config,
                rpc_retries=rpc_retries or platform_cfg.rpc_retries,
                http_proxy_url=http_proxy_url or platform_cfg.http_proxy_url,
            )

        root_dir = root_dir or get_cwd_editable_install() or Path.cwd()
        _init_config = _InitConfig(
            root_dir=root_dir,
            project=project or task_cfg.project,
            domain=domain or task_cfg.domain,
            client=client,
            storage=storage,
            org=org or task_cfg.org,
        )


def _get_init_config() -> Optional[_InitConfig]:
    """
    Get the current initialization configuration. Thread-safe implementation.

    :return: The current InitData if initialized, None otherwise
    """
    with _init_lock:
        return _init_config


def get_common_config() -> CommonInit:
    """
    Get the current initialization configuration. Thread-safe implementation.

    :return: The current InitData if initialized, None otherwise
    """
    cfg = _get_init_config()
    if cfg is None:
        raise InitializationError(
            "StorageNotInitializedError",
            "user",
            "Configuration has not been initialized. Call flyte.init() with a valid endpoint or",
            " api-key before using this function.",
        )
    return cfg


def get_storage() -> Storage:
    """
    Get the current storage configuration. Thread-safe implementation.

    :return: The current storage configuration
    """
    cfg = _get_init_config()
    if cfg is None:
        raise InitializationError(
            "StorageNotInitializedError",
            "user",
            "Configuration has not been initialized. Call flyte.init() with a valid endpoint or",
            " api-key before using this function.",
        )
    if cfg.storage is None:
        # return default local storage
        return typing.cast(Storage, cfg.replace(storage=Storage()).storage)
    return cfg.storage


def get_client() -> ClientSet:
    """
    Get the current client. Thread-safe implementation.

    :return: The current client
    """
    cfg = _get_init_config()
    if cfg is None or cfg.client is None:
        raise InitializationError(
            "ClientNotInitializedError",
            "user",
            "Client has not been initialized. Call flyte.init() with a valid endpoint or"
            " api-key before using this function.",
        )
    return cfg.client


def is_initialized() -> bool:
    """
    Check if the system has been initialized.

    :return: True if initialized, False otherwise
    """
    return _get_init_config() is not None


def initialize_in_cluster(storage: Storage | None = None) -> None:
    """
    Initialize the system for in-cluster execution. This is a placeholder function and does not perform any actions.

    :return: None
    """
    init(storage=storage)


# Define a generic type variable for the decorated function
T = TypeVar("T", bound=Callable)


def requires_client(func: T) -> T:
    """
    Decorator that checks if the client has been initialized before executing the function.
    Raises InitializationError if the client is not initialized.

    :param func: Function to decorate
    :return: Decorated function that checks for initialization
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> T:
        init_config = _get_init_config()
        if init_config is None or init_config.client is None:
            raise InitializationError(
                "ClientNotInitializedError",
                "user",
                f"Function '{func.__name__}' requires client to be initialized. "
                f"Call flyte.init() with a valid endpoint or api-key before using this function.",
            )
        return func(*args, **kwargs)

    return typing.cast(T, wrapper)


def requires_storage(func: T) -> T:
    """
    Decorator that checks if the storage has been initialized before executing the function.
    Raises InitializationError if the storage is not initialized.

    :param func: Function to decorate
    :return: Decorated function that checks for initialization
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if _get_init_config() is None or _get_init_config().storage is None:
            raise InitializationError(
                "StorageNotInitializedError",
                "user",
                f"Function '{func.__name__}' requires storage to be initialized. "
                f"Call flyte.init() with a valid storage configuration before using this function.",
            )
        return func(*args, **kwargs)

    return typing.cast(T, wrapper)


def requires_upload_location(func: T) -> T:
    """
    Decorator that checks if the storage has been initialized before executing the function.
    Raises InitializationError if the storage is not initialized.

    :param func: Function to decorate
    :return: Decorated function that checks for initialization
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> T:
        from ._context import internal_ctx

        ctx = internal_ctx()
        if not ctx.raw_data:
            raise InitializationError(
                "No upload path configured",
                "user",
                f"Function '{func.__name__}' requires client to be initialized. "
                f"Call flyte.init() with storage configuration before using this function.",
            )
        return func(*args, **kwargs)

    return typing.cast(T, wrapper)


def requires_initialization(func: T) -> T:
    """
    Decorator that checks if the system has been initialized before executing the function.
    Raises InitializationError if the system is not initialized.

    :param func: Function to decorate
    :return: Decorated function that checks for initialization
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> T:
        if not is_initialized():
            raise InitializationError(
                "NotInitConfiguredError",
                "user",
                f"Function '{func.__name__}' requires initialization. Call flyte.init() before using this function.",
            )
        return func(*args, **kwargs)

    return typing.cast(T, wrapper)


async def _init_for_testing(
    project: str | None = None,
    domain: str | None = None,
    root_dir: Path | None = None,
    log_level: int | None = None,
    client: ClientSet | None = None,
):
    from flyte._utils.helpers import get_cwd_editable_install

    global _init_config  # noqa: PLW0603

    if log_level:
        initialize_logger(log_level=log_level)

    with _init_lock:
        root_dir = root_dir or get_cwd_editable_install() or Path.cwd()
        _init_config = _InitConfig(
            root_dir=root_dir,
            project=project,
            domain=domain,
            client=client,
        )


def replace_client(client):
    global _init_config  # noqa: PLW0603

    with _init_lock:
        _init_config = _init_config.replace(client=client)
