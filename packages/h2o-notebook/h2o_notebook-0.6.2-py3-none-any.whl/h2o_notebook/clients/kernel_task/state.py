from enum import Enum

from h2o_notebook.gen.model.v1_kernel_task_state import V1KernelTaskState


class KernelTaskState(Enum):
    STATE_UNSPECIFIED = "STATE_UNSPECIFIED"
    STATE_QUEUED = "STATE_QUEUED"
    STATE_EXECUTING = "STATE_EXECUTING"
    STATE_COMPLETE_ERROR = "STATE_COMPLETE_ERROR"
    STATE_COMPLETE_SUCCESS = "STATE_COMPLETE_SUCCESS"
    STATE_CANCELLED = "STATE_CANCELLED"

    def to_api_object(self) -> V1KernelTaskState:
        return V1KernelTaskState(self.name)


def from_api_object(kernel_task_state: V1KernelTaskState) -> KernelTaskState:
    return KernelTaskState(str(kernel_task_state))
