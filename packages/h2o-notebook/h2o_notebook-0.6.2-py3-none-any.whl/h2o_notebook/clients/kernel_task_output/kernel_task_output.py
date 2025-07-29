import base64
import pprint
from typing import List
from typing import Optional

from h2o_notebook.gen.model.attachment_attachment_data import AttachmentAttachmentData
from h2o_notebook.gen.model.kernel_task_output_attachment import (
    KernelTaskOutputAttachment,
)
from h2o_notebook.gen.model.v1_kernel_task_output import V1KernelTaskOutput


class AttachmentData:
    """
    Additional non-text data produced by the KernelTask.
    """

    def __init__(
        self,
        mime_type: str = "",
        data: bytes = b'',
    ):
        """
        Args:
            mime_type (str): The MIME type of the data.
            data (bytes): The data bytes.
        """
        self.mime_type = mime_type
        self.data = data

    def __repr__(self) -> str:
        return pprint.pformat(self.__dict__)

    def __eq__(self, other):
        if isinstance(other, AttachmentData):
            return self.mime_type == other.mime_type and self.data == other.data
        return False

    def __hash__(self):
        return hash((self.mime_type, self.data))


def from_api_object_attachment_data(api_object: AttachmentAttachmentData) -> AttachmentData:
    return AttachmentData(
        mime_type=api_object.mime_type,
        data=base64.b64decode(api_object.data),
    )


class Attachment:
    """
    KernelTaskOutput attachment.
    """

    def __init__(
        self,
        data: List[AttachmentData] = None,
    ):
        """
        Args:
            data (List[AttachmentData]): All available representations of the attachment data.
        """
        if data is None:
            data = []

        self.data = data

    def __repr__(self) -> str:
        return pprint.pformat(self.__dict__)


def from_api_object_attachment(api_object: KernelTaskOutputAttachment) -> Attachment:
    return Attachment(
        data=[from_api_object_attachment_data(api_object=a) for a in api_object.data],
    )


class KernelTaskOutput:
    """
    KernelTaskOutput is an aggregated output of a KernelTask.
    """

    def __init__(
        self,
        name: str = "",
        stdout: Optional[str] = None,
        stderr: Optional[str] = None,
        attachments: List[Attachment] = None,
    ):
        """
        Args:
            name (str): Resource name of the KernelTaskOutput. Format is `workspaces/*/kernels/*/tasks/*/output`.
            stdout (str): Aggregated standard output of the KernelTask.
                It may be populated when the KernelTask is running.
                Only after the task has completed it is guaranteed to not change further.
            stderr (str): Aggregated standard error output of the KernelTask.
                It may be populated when the KernelTask is running.
                Only after the task has completed it is guaranteed to not change further.
            attachments (List[Attachment]): List of additional non-text data produced by the KernelTask.
        """
        if attachments is None:
            attachments = []

        self.name = name
        self.stdout = stdout
        self.stderr = stderr
        self.attachments = attachments

    def __repr__(self) -> str:
        return pprint.pformat(self.__dict__)


def from_api_object(api_object: V1KernelTaskOutput) -> KernelTaskOutput:
    return KernelTaskOutput(
        name=api_object.name,
        stdout=api_object.stdout,
        stderr=api_object.stderr,
        attachments=[from_api_object_attachment(api_object=a) for a in api_object.attachments],
    )
