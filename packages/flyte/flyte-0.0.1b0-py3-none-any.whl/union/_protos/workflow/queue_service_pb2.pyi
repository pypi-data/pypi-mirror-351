from union._protos.validate.validate import validate_pb2 as _validate_pb2
from union._protos.workflow import run_definition_pb2 as _run_definition_pb2
from union._protos.workflow import task_definition_pb2 as _task_definition_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class EnqueueActionRequest(_message.Message):
    __slots__ = ["action_id", "parent_action_name", "task_id", "task_spec", "input_uri", "output_uri", "group", "subject"]
    ACTION_ID_FIELD_NUMBER: _ClassVar[int]
    PARENT_ACTION_NAME_FIELD_NUMBER: _ClassVar[int]
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    TASK_SPEC_FIELD_NUMBER: _ClassVar[int]
    INPUT_URI_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_URI_FIELD_NUMBER: _ClassVar[int]
    GROUP_FIELD_NUMBER: _ClassVar[int]
    SUBJECT_FIELD_NUMBER: _ClassVar[int]
    action_id: _run_definition_pb2.ActionIdentifier
    parent_action_name: str
    task_id: _task_definition_pb2.TaskIdentifier
    task_spec: _task_definition_pb2.TaskSpec
    input_uri: str
    output_uri: str
    group: str
    subject: str
    def __init__(self, action_id: _Optional[_Union[_run_definition_pb2.ActionIdentifier, _Mapping]] = ..., parent_action_name: _Optional[str] = ..., task_id: _Optional[_Union[_task_definition_pb2.TaskIdentifier, _Mapping]] = ..., task_spec: _Optional[_Union[_task_definition_pb2.TaskSpec, _Mapping]] = ..., input_uri: _Optional[str] = ..., output_uri: _Optional[str] = ..., group: _Optional[str] = ..., subject: _Optional[str] = ...) -> None: ...

class EnqueueActionResponse(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class AbortQueuedActionRequest(_message.Message):
    __slots__ = ["action_id"]
    ACTION_ID_FIELD_NUMBER: _ClassVar[int]
    action_id: _run_definition_pb2.ActionIdentifier
    def __init__(self, action_id: _Optional[_Union[_run_definition_pb2.ActionIdentifier, _Mapping]] = ...) -> None: ...

class AbortQueuedActionResponse(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class HeartbeatRequest(_message.Message):
    __slots__ = ["worker_id", "cluster_id", "active_action_ids", "terminal_action_ids", "organization", "available_capacity"]
    WORKER_ID_FIELD_NUMBER: _ClassVar[int]
    CLUSTER_ID_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_ACTION_IDS_FIELD_NUMBER: _ClassVar[int]
    TERMINAL_ACTION_IDS_FIELD_NUMBER: _ClassVar[int]
    ORGANIZATION_FIELD_NUMBER: _ClassVar[int]
    AVAILABLE_CAPACITY_FIELD_NUMBER: _ClassVar[int]
    worker_id: str
    cluster_id: str
    active_action_ids: _containers.RepeatedCompositeFieldContainer[_run_definition_pb2.ActionIdentifier]
    terminal_action_ids: _containers.RepeatedCompositeFieldContainer[_run_definition_pb2.ActionIdentifier]
    organization: str
    available_capacity: int
    def __init__(self, worker_id: _Optional[str] = ..., cluster_id: _Optional[str] = ..., active_action_ids: _Optional[_Iterable[_Union[_run_definition_pb2.ActionIdentifier, _Mapping]]] = ..., terminal_action_ids: _Optional[_Iterable[_Union[_run_definition_pb2.ActionIdentifier, _Mapping]]] = ..., organization: _Optional[str] = ..., available_capacity: _Optional[int] = ...) -> None: ...

class HeartbeatResponse(_message.Message):
    __slots__ = ["new_leases", "aborted_action_ids", "finalized_action_ids"]
    NEW_LEASES_FIELD_NUMBER: _ClassVar[int]
    ABORTED_ACTION_IDS_FIELD_NUMBER: _ClassVar[int]
    FINALIZED_ACTION_IDS_FIELD_NUMBER: _ClassVar[int]
    new_leases: _containers.RepeatedCompositeFieldContainer[Lease]
    aborted_action_ids: _containers.RepeatedCompositeFieldContainer[_run_definition_pb2.ActionIdentifier]
    finalized_action_ids: _containers.RepeatedCompositeFieldContainer[_run_definition_pb2.ActionIdentifier]
    def __init__(self, new_leases: _Optional[_Iterable[_Union[Lease, _Mapping]]] = ..., aborted_action_ids: _Optional[_Iterable[_Union[_run_definition_pb2.ActionIdentifier, _Mapping]]] = ..., finalized_action_ids: _Optional[_Iterable[_Union[_run_definition_pb2.ActionIdentifier, _Mapping]]] = ...) -> None: ...

class StreamLeasesRequest(_message.Message):
    __slots__ = ["worker_id"]
    WORKER_ID_FIELD_NUMBER: _ClassVar[int]
    worker_id: str
    def __init__(self, worker_id: _Optional[str] = ...) -> None: ...

class StreamLeasesResponse(_message.Message):
    __slots__ = ["leases"]
    LEASES_FIELD_NUMBER: _ClassVar[int]
    leases: _containers.RepeatedCompositeFieldContainer[Lease]
    def __init__(self, leases: _Optional[_Iterable[_Union[Lease, _Mapping]]] = ...) -> None: ...

class Lease(_message.Message):
    __slots__ = ["action_id", "parent_action_name", "task_id", "task_spec", "input_uri", "output_uri", "group", "subject", "previous_state"]
    ACTION_ID_FIELD_NUMBER: _ClassVar[int]
    PARENT_ACTION_NAME_FIELD_NUMBER: _ClassVar[int]
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    TASK_SPEC_FIELD_NUMBER: _ClassVar[int]
    INPUT_URI_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_URI_FIELD_NUMBER: _ClassVar[int]
    GROUP_FIELD_NUMBER: _ClassVar[int]
    SUBJECT_FIELD_NUMBER: _ClassVar[int]
    PREVIOUS_STATE_FIELD_NUMBER: _ClassVar[int]
    action_id: _run_definition_pb2.ActionIdentifier
    parent_action_name: str
    task_id: _task_definition_pb2.TaskIdentifier
    task_spec: _task_definition_pb2.TaskSpec
    input_uri: str
    output_uri: str
    group: str
    subject: str
    previous_state: str
    def __init__(self, action_id: _Optional[_Union[_run_definition_pb2.ActionIdentifier, _Mapping]] = ..., parent_action_name: _Optional[str] = ..., task_id: _Optional[_Union[_task_definition_pb2.TaskIdentifier, _Mapping]] = ..., task_spec: _Optional[_Union[_task_definition_pb2.TaskSpec, _Mapping]] = ..., input_uri: _Optional[str] = ..., output_uri: _Optional[str] = ..., group: _Optional[str] = ..., subject: _Optional[str] = ..., previous_state: _Optional[str] = ...) -> None: ...
