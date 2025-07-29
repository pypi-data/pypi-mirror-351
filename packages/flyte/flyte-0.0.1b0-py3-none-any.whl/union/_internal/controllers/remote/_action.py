from __future__ import annotations

from dataclasses import dataclass

from flyteidl.core import execution_pb2

from union._datastructures import GroupData
from union._protos.workflow import run_definition_pb2, state_service_pb2, task_definition_pb2


@dataclass
class Action:
    """
    Coroutine safe, as we never do await operations in any method.
    Holds the inmemory state of a task. It is combined representation of local and remote states.
    """

    action_id: run_definition_pb2.ActionIdentifier
    parent_action_name: str
    friendly_name: str | None = None
    group: GroupData | None = None
    task: task_definition_pb2.TaskSpec | None = None
    inputs_uri: str | None = None
    outputs_uri: str | None = None
    err: execution_pb2.ExecutionError | None = None
    phase: run_definition_pb2.Phase | None = None
    started: bool = False
    retries: int = 0
    client_err: Exception | None = None  # This error is set when something goes wrong in the controller.

    @property
    def name(self) -> str:
        return self.action_id.name

    @property
    def run_name(self) -> str:
        return self.action_id.run.name

    def is_terminal(self) -> bool:
        """Check if resource has reached terminal state"""
        if self.phase is None:
            return False
        return self.phase in [
            run_definition_pb2.Phase.PHASE_FAILED,
            run_definition_pb2.Phase.PHASE_SUCCEEDED,
            run_definition_pb2.Phase.PHASE_ABORTED,
            run_definition_pb2.Phase.PHASE_TIMED_OUT,
        ]

    def increment_retries(self):
        self.retries += 1

    def is_started(self) -> bool:
        """Check if resource has been started."""
        return self.started

    def mark_started(self):
        self.started = True
        self.task = None

    def merge_state(self, obj: state_service_pb2.ActionUpdate):
        """
        This method is invoked when the watch API sends an update about the state of the action. We need to merge
        the state of the action with the current state of the action. It is possible that we have no phase information
        prior to this.
        :param obj:
        :return:
        """
        if self.phase != obj.phase:
            self.phase = obj.phase
            self.err = obj.error if obj.HasField("error") else None
        self.started = True

    def merge_in_action_from_submit(self, action: Action):
        """
        This method is invoked when parent_action submits an action that was observed previously observed from the
         watch. We need to merge in the contents of the action, while preserving the observed phase.

        :param action: The submitted action
        """
        self.outputs_uri = action.outputs_uri
        self.inputs_uri = action.inputs_uri
        self.group = action.group
        self.friendly_name = action.friendly_name
        if not self.started:
            self.task = action.task

    def set_client_error(self, exc: Exception):
        self.client_err = exc

    def has_error(self) -> bool:
        return self.client_err is not None or self.err is not None

    @classmethod
    def from_task(
        cls,
        parent_action_name: str,
        sub_action_id: run_definition_pb2.ActionIdentifier,
        group_data: GroupData,
        task_spec: task_definition_pb2.TaskSpec,
        inputs_uri: str,
        outputs_prefix_uri: str,
    ) -> Action:
        return cls(
            action_id=sub_action_id,
            parent_action_name=parent_action_name,
            friendly_name=task_spec.task_template.id.name,
            group=group_data,
            task=task_spec,
            inputs_uri=inputs_uri,
            outputs_uri=outputs_prefix_uri,
        )

    @classmethod
    def from_state(cls, parent_action_name: str, obj: state_service_pb2.ActionUpdate) -> Action:
        """
        This creates a new action, from the watch api. This is possible in the case of a recovery, where the
        stateservice knows about future actions and sends this information to the informer. We may not have encountered
        the "task" itself yet, but we know about the action id and the state of the action.

        :param parent_action_name:
        :param obj:
        :return:
        """
        return cls(
            action_id=obj.action_id,
            parent_action_name=parent_action_name,
            phase=obj.phase,
            started=True,
            err=obj.error if obj.HasField("error") else None,
        )
