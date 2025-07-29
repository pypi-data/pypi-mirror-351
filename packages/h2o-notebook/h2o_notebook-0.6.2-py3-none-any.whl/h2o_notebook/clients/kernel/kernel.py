import pprint
from datetime import datetime
from typing import Dict
from typing import Optional

from h2o_notebook.clients.kernel.kernel_image_info import KernelImageInfo
from h2o_notebook.clients.kernel.kernel_image_info import (
    from_api_object as from_kernel_image_info_api_object,
)
from h2o_notebook.clients.kernel.kernel_template_info import KernelTemplateInfo
from h2o_notebook.clients.kernel.kernel_template_info import (
    from_api_object as from_kernel_template_api_object,
)
from h2o_notebook.clients.kernel.state import KernelState
from h2o_notebook.clients.kernel.type import KernelType
from h2o_notebook.gen.model.v1_kernel import V1Kernel
from h2o_notebook.gen.model.v1_kernel_image_info import V1KernelImageInfo
from h2o_notebook.gen.model.v1_kernel_template_info import V1KernelTemplateInfo


class Kernel:
    """
    Kernel is a virtual machine that runs a language interpreter and provides interactive access.
    """

    def __init__(
        self,
        kernel_image: str,
        kernel_template: str,
        name: str = "",
        display_name: str = "",
        notebook_kernel_spec: str = "",
        environmental_variables: Dict[str, str] = None,
        creator: str = "",
        creator_display_name: str = "",
        state: KernelState = KernelState.STATE_UNSPECIFIED,
        kernel_type: KernelType = KernelType.TYPE_UNSPECIFIED,
        current_task: str = "",
        current_task_sequence_number: int = 0,
        task_queue_size: int = 0,
        create_time: datetime = None,
        failure_reason: str = "",
        kernel_template_info: KernelTemplateInfo = None,
        kernel_image_info: KernelImageInfo = None,
        last_activity_time: Optional[datetime] = None,
    ):
        """
        Args:
            kernel_image (str): Resource name of the KernelImage that is used to create the Kernel.
                Format is `workspaces/*/kernelImages/*`.
            kernel_template (str): Resource name of the KernelTemplate that is used to create the Kernel.
                Format is `workspaces/*/kernelTemplates/*`.
            name (str, optional): Resource name of the Kernel. Format is `workspaces/*/kernels/*`.
            display_name (str, optional): Human-readable name of the Kernel.
            notebook_kernel_spec (str, optional): Resource name of the NotebookKernelSpec that was used
                to create the Kernel.
                Only set for TYPE_NOTEBOOK kernels.
                Format is `workspaces/*/notebookKernelSpecs/*`.
            environmental_variables (Dict[str, str], optional): Map of additional environmental variables
                that will be set in the Kernel.
                This set of environmental variables take precedence over the ones defined in the KernelTemplate.
            creator (str, optional): Name of an entity that created the Kernel.
            creator_display_name (str, optional): Human-readable name of creator.
            state (KernelState, optional): The current state of the Kernel.
            kernel_type (KernelType, optional): The type of the Kernel.
            current_task (str, optional): The resource name of the KernelTask that is currently being executed
                by the Kernel.
                Format is `kernels/{kernel}/tasks/{task}`.
            current_task_sequence_number (int, optional): Sequential number of the KernelTask that is currently
                being executed by the Kernel.
                Set to 0 if no KernelTask is currently being executed.
            task_queue_size (int, optional): Number of KernelTasks that are currently queued for execution by the Kernel.
            create_time (datetime, optional): Time when the Kernel was created.
            failure_reason (str, optional): Reason why the Kernel failed.
            kernel_template_info (KernelTemplateInfo, optional): KernelTemplate data taken at the time of Kernel creation.
            kernel_image_info (KernelImageInfo, optional): KernelImage data taken at the time of Kernel creation.
            last_activity_time (Optional[datetime], optional): Time when the Kernel was last active executing a KernelTask.
        """
        if environmental_variables is None:
            environmental_variables = {}

        self.kernel_image = kernel_image
        self.kernel_template = kernel_template
        self.name = name
        self.display_name = display_name
        self.notebook_kernel_spec = notebook_kernel_spec
        self.environmental_variables = environmental_variables
        self.creator = creator
        self.creator_display_name = creator_display_name
        self.state = state
        self.kernel_type = kernel_type
        self.current_task = current_task
        self.current_task_sequence_number = current_task_sequence_number
        self.task_queue_size = task_queue_size
        self.create_time = create_time
        self.failure_reason = failure_reason
        self.kernel_template_info = kernel_template_info
        self.kernel_image_info = kernel_image_info
        self.last_activity_time = last_activity_time

    def get_kernel_id(self):
        segments = self.name.split("/")
        if len(segments) != 4:
            return ""

        return segments[3]

    def __repr__(self) -> str:
        return pprint.pformat(self.__dict__)

    def to_api_object(self) -> V1Kernel:
        kernel_template_info: V1KernelTemplateInfo = V1KernelTemplateInfo()
        if self.kernel_template_info is not None:
            kernel_template_info = self.kernel_template_info.to_api_object()

        kernel_image_info: V1KernelImageInfo = V1KernelImageInfo()
        if self.kernel_image_info is not None:
            kernel_image_info = self.kernel_image_info.to_api_object()

        return V1Kernel(
            kernel_image=self.kernel_image,
            kernel_template=self.kernel_template,
            display_name=self.display_name,
            environmental_variables=self.environmental_variables,
            state=self.state.to_api_object(),
            type=self.kernel_type.to_api_object(),
            kernel_template_info=kernel_template_info,
            kernel_image_info=kernel_image_info,
        )


def from_api_object(api_object: V1Kernel) -> Kernel:
    return Kernel(
        name=api_object.name,
        kernel_image=api_object.kernel_image,
        kernel_template=api_object.kernel_template,
        display_name=api_object.display_name,
        notebook_kernel_spec=api_object.notebook_kernel_spec,
        environmental_variables=api_object.environmental_variables,
        creator=api_object.creator,
        creator_display_name=api_object.creator_display_name,
        state=KernelState(str(api_object.state)),
        kernel_type=KernelType(str(api_object.type)),
        current_task=api_object.current_task,
        current_task_sequence_number=api_object.current_task_sequence_number,
        task_queue_size=api_object.task_queue_size,
        create_time=api_object.create_time,
        failure_reason=api_object.failure_reason,
        kernel_image_info=from_kernel_image_info_api_object(api_object.kernel_image_info),
        kernel_template_info=from_kernel_template_api_object(api_object.kernel_template_info),
        last_activity_time=api_object.last_activity_time,
    )
