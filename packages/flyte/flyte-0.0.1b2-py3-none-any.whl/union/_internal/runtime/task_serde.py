"""
This module provides functionality to serialize and deserialize tasks to and from the wire format.
It includes a Resolver interface for loading tasks, and functions to load classes and tasks.
"""

import importlib
from typing import List, Optional, Type

from flyteidl.core import identifier_pb2, literals_pb2, security_pb2, tasks_pb2
from google.protobuf import duration_pb2, wrappers_pb2

from union._cache.cache import VersionParameters, cache_from_request
from union._datastructures import SerializationContext
from union._internal.resolvers.common import Resolver
from union._logging import logger
from union._protos.workflow import task_definition_pb2
from union._secret import SecretRequest, secrets_from_request
from union._task import AsyncFunctionTaskTemplate, TaskTemplate

from ..._timeout import timeout_from_request
from .resources_serde import get_proto_extended_resources, get_proto_resources
from .types_serde import transform_native_to_typed_interface


def load_class(qualified_name) -> Type:
    """
    Load a class from a qualified name. The qualified name should be in the format 'module.ClassName'.
    :param qualified_name: The qualified name of the class to load.
    :return: The class object.
    """
    module_name, class_name = qualified_name.rsplit(".", 1)  # Split module and class
    module = importlib.import_module(module_name)  # Import the module
    return getattr(module, class_name)  # Retrieve the class


def load_task(resolver: str, *resolver_args: str) -> TaskTemplate:
    """
    Load a task from a resolver. This is a placeholder function.

    :param resolver: The resolver to use to load the task.
    :param resolver_args: Arguments to pass to the resolver.
    :return: The loaded task.
    """
    resolver_class = load_class(resolver)
    resolver_instance = resolver_class()
    return resolver_instance.load_task(resolver_args)


def get_task_loader_args(resolver: Resolver, task: TaskTemplate) -> List[str]:
    """
    Get the task loader args from a resolver. This is a placeholder function.

    :param resolver: The resolver to use to load the task.
    :param task: The task to get the loader args for.

    :return: The loader args for the task.
    """
    return resolver.loader_args(task)


def translate_task_to_wire(
    task: TaskTemplate, serialization_context: SerializationContext
) -> task_definition_pb2.TaskSpec:
    """
    Translate a task to a wire format. This is a placeholder function.

    :param task: The task to translate.
    :param serialization_context: The serialization context to use for the translation.

    :return: The translated task.
    """
    # Placeholder implementation
    return get_proto_task(task, serialization_context)


def get_security_context(secrets: Optional[SecretRequest]) -> Optional[security_pb2.SecurityContext]:
    """
    Get the security context from a list of secrets. This is a placeholder function.

    :param secrets: The list of secrets to use for the security context.

    :return: The security context.
    """
    if secrets is None:
        return None

    secret_list = secrets_from_request(secrets)
    return security_pb2.SecurityContext(
        secrets=[
            security_pb2.Secret(
                group=secret.group,
                key=secret.key,
                mount_requirement=(
                    security_pb2.Secret.MountType.ENV_VAR if secret.as_env_var else security_pb2.Secret.MountType.FILE
                ),
                env_var=secret.as_env_var,
            )
            for secret in secret_list
        ]
    )


def get_proto_task(task: TaskTemplate, serialize_context: SerializationContext) -> task_definition_pb2.TaskSpec:
    task_id = identifier_pb2.Identifier(
        resource_type=identifier_pb2.ResourceType.TASK,
        project=serialize_context.project,
        domain=serialize_context.domain,
        org=serialize_context.org,
        name=task.name,
        version=serialize_context.version,
    )

    # TODO, there will be tasks that do not have images, handle that case
    # if task.parent_env is None:
    # raise ValueError(f"Task {task.name} must have a parent environment")

    #
    # This pod will be incorrect when doing fast serialize
    #
    pod = None
    sql = None
    container = _get_urun_container(serialize_context, task)
    # pod = task.get_k8s_pod(serialize_context)
    extra_config = {}
    custom = {}
    task_cache = cache_from_request(task.cache)

    # -------------- CACHE HANDLING ----------------------
    task_cache = cache_from_request(task.cache)
    cache_enabled = task_cache.is_enabled()
    cache_version = None

    if task_cache.is_enabled():
        logger.debug(f"Cache enabled for task {task.name}")
        if serialize_context.code_bundle and serialize_context.code_bundle.pkl:
            logger.debug(f"Detected pkl bundle for task {task.name}, using computed version as cache version")
            cache_version = serialize_context.code_bundle.computed_version
        else:
            version_parameters = None
            if isinstance(task, AsyncFunctionTaskTemplate):
                version_parameters = VersionParameters(func=task.func, image=task.image)
            else:
                version_parameters = VersionParameters(func=None, image=task.image)
            cache_version = task_cache.get_version(version_parameters)
            logger.debug(f"Cache version for task {task.name} is {cache_version}")
    else:
        logger.debug(f"Cache disabled for task {task.name}")

    tt = tasks_pb2.TaskTemplate(
        id=task_id,
        type=task.task_type,
        metadata=tasks_pb2.TaskMetadata(
            discoverable=cache_enabled,
            discovery_version=cache_version,
            cache_serializable=task_cache.serialize,
            cache_ignore_input_vars=task.cache.ignored_inputs,
            runtime=tasks_pb2.RuntimeMetadata(),
            retries=literals_pb2.RetryStrategy(retries=task.retries.count),
            timeout=duration_pb2.Duration(seconds=timeout_from_request(task.timeout).max_runtime.seconds)
            if task.timeout
            else None,
            pod_template_name=task.pod_template if task.pod_template and isinstance(task.pod_template, str) else None,
            interruptible=task.interruptable,
            generates_deck=wrappers_pb2.BoolValue(value=False),  # TODO add support for reports
        ),
        interface=transform_native_to_typed_interface(task.native_interface),
        custom=custom,
        container=container,
        task_type_version=task.task_type_version,
        security_context=get_security_context(task.secrets),
        config=extra_config,
        k8s_pod=pod,
        sql=sql,
        extended_resources=get_proto_extended_resources(task.resources),
    )
    return task_definition_pb2.TaskSpec(task_template=tt)


def _get_urun_container(
    serialize_context: SerializationContext, task_template: TaskTemplate
) -> Optional[tasks_pb2.Container]:
    env = (
        [literals_pb2.KeyValuePair(key=k, value=v) for k, v in task_template.env.items()] if task_template.env else None
    )
    resources = get_proto_resources(task_template.resources)
    # pr: under what conditions should this return None?
    image_id = task_template.image.identifier
    if not serialize_context.image_cache or image_id not in serialize_context.image_cache.image_lookup:
        # This computes the image uri, computing hashes as necessary so can fail if done remotely.
        img_uri = task_template.image.uri
    else:
        img_uri = serialize_context.image_cache.image_lookup[image_id]

    return tasks_pb2.Container(
        image=img_uri,
        command=[],
        args=task_template.container_args(serialize_context),
        resources=resources,
        env=env,
        data_config=task_template.data_loading_config(serialize_context),
        config=task_template.config(serialize_context),
    )
