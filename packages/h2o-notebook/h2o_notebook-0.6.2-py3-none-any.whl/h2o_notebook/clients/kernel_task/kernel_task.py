import pprint
from datetime import datetime
from typing import Optional

from h2o_notebook.clients.kernel_task.state import KernelTaskState
from h2o_notebook.gen.model.v1_kernel_task import V1KernelTask


class KernelTask:
    """
    KernelTask is a task that is executed on a Kernel.
    Kernel processes one task at a time in the order they are received.
    """

    def __init__(
        self,
        code: str,
        name: str = "",
        state: KernelTaskState = KernelTaskState.STATE_UNSPECIFIED,
        sequence_number: int = 0,
        tasks_ahead_count: int = 0,
        error: str = "",
        error_value: str = "",
        traceback: str = "",
        create_time: datetime = None,
        execution_start_time: Optional[datetime] = None,
        complete_time: Optional[datetime] = None,
    ):
        """
        Args:
            code (str): The code to be executed by the Kernel.
            name (str, optional): Resource name. Format is `workspaces/*/kernels/*/tasks/*`.
            state (KernelTaskState, optional): The current state of the KernelTask.
            sequence_number (int, optional): The sequential number assigned to the KernelTask by the Kernel.
                The first KernelTask submitted to a Kernel will have sequence_number 1.
            tasks_ahead_count (int, optional): The number of KernelTasks ahead of this KernelTask
                in the KernelTasks queue.
                When not queued, this field is 0.
            error (str, optional): When the KernelTask has completed with an error,
                this field will be populated with the error name.
                For example: "NameError".
            error_value (str, optional): When the KernelTask has completed with an error,
                this field will be populated with the error value.
                For example: "name 'x' is not defined".
            traceback (str, optional): When the KernelTask has completed with an error,
                this field will be populated with the traceback.
            create_time (datetime, optional): Time when the KernelTask was created.
            execution_start_time (Optional[datetime], optional): Time when the KernelTask started executing.
            complete_time (Optional[datetime], optional): Time when the KernelTask completed.
        """
        self.code = code
        self.name = name
        self.state = state
        self.sequence_number = sequence_number
        self.tasks_ahead_count = tasks_ahead_count
        self.error = error
        self.error_value = error_value
        self.traceback = traceback
        self.create_time = create_time
        self.execution_start_time = execution_start_time
        self.complete_time = complete_time

    def get_kernel_id(self):
        segments = self.name.split("/")
        if len(segments) != 6:
            return ""

        return segments[3]

    def get_kernel_task_id(self):
        segments = self.name.split("/")
        if len(segments) != 6:
            return ""

        return segments[5]

    def __repr__(self) -> str:
        return pprint.pformat(self.__dict__)

    def to_api_object(self) -> V1KernelTask:
        return V1KernelTask(
            code=self.code,
        )


def from_api_object(api_object: V1KernelTask) -> KernelTask:
    return KernelTask(
        name=api_object.name,
        code=api_object.code,
        state=KernelTaskState(str(api_object.state)),
        sequence_number=api_object.sequence_number,
        tasks_ahead_count=api_object.tasks_ahead_count,
        error=api_object.error,
        error_value=api_object.error_value,
        traceback=api_object.traceback,
        create_time=api_object.create_time,
        execution_start_time=api_object.execution_start_time,
        complete_time=api_object.complete_time,
    )
