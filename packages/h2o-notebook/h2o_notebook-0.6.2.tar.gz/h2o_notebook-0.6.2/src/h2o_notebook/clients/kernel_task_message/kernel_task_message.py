import pprint
from datetime import datetime
from typing import Optional

from h2o_notebook.clients.kernel_task_message.display_message import DisplayMessage
from h2o_notebook.clients.kernel_task_message.display_message import (
    from_display_message_api_object,
)
from h2o_notebook.gen.model.kernel_task_message_stream_message_type import (
    KernelTaskMessageStreamMessageType,
)
from h2o_notebook.gen.model.v1_kernel_task_message import V1KernelTaskMessage


class KernelTaskMessage:
    """
    KernelTaskMessage is a partial output of a KernelTask.
    It contains stream messages (stdout/stderr) or a display messages (images, sound, HTML, etc.).
    """

    def __init__(
        self,
        name: str = "",
        create_time: datetime = None,
        std_out: Optional[str] = None,
        std_err: Optional[str] = None,
        display_message: Optional[DisplayMessage] = None,
    ):
        """
        Args:
            name (str): Resource name of the KernelTaskMessage. Format is `workspaces/*/kernels/*/tasks/*/messages/*`.
            create_time (datetime): Time when the KernelTaskMessage was created.
            std_out (Optional[str]): Standard output stream message.
            std_err (Optional[str]): Standard error stream message.
            display_message (Optional[DisplayMessage]): Additional metadata to display data.
        """
        self.name = name
        self.create_time = create_time
        self.std_out = std_out
        self.std_err = std_err
        self.display_message = display_message

    def __repr__(self) -> str:
        return pprint.pformat(self.__dict__)


def from_api_object(api_object: V1KernelTaskMessage) -> KernelTaskMessage:
    std_out = None
    std_err = None
    display_message = None

    if api_object.stream:
        if api_object.stream.type == KernelTaskMessageStreamMessageType("TYPE_STDOUT"):
            std_out = api_object.stream.data
        if api_object.stream.type == KernelTaskMessageStreamMessageType("TYPE_STDERR"):
            std_err = api_object.stream.data

    if api_object.display:
        display_message = from_display_message_api_object(api_object=api_object.display)

    return KernelTaskMessage(
        name=api_object.name,
        std_out=std_out,
        std_err=std_err,
        display_message=display_message,
        create_time=api_object.create_time,
    )
