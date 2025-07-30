from enum import Enum

from h2o_notebook.gen.model.v1_kernel_state import V1KernelState


class KernelState(Enum):
    STATE_UNSPECIFIED = "STATE_UNSPECIFIED"
    STATE_STARTING = "STATE_STARTING"
    STATE_RUNNING_IDLE = "STATE_RUNNING_IDLE"
    STATE_RUNNING_BUSY = "STATE_RUNNING_BUSY"
    STATE_FAILED = "STATE_FAILED"
    STATE_TERMINATING = "STATE_TERMINATING"
    STATE_TERMINATED = "STATE_TERMINATED"

    def to_api_object(self) -> V1KernelState:
        return V1KernelState(self.name)


def from_api_object(kernel_state: V1KernelState) -> KernelState:
    return KernelState(str(kernel_state))
