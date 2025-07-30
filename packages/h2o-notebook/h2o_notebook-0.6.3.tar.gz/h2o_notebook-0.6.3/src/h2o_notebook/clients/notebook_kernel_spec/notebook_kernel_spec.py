import pprint

from h2o_notebook.gen.model.required_notebook_kernel_spec_resource import (
    RequiredNotebookKernelSpecResource,
)
from h2o_notebook.gen.model.v1_notebook_kernel_spec import V1NotebookKernelSpec


class NotebookKernelSpec:
    """
    NotebookKernelSpec represents a Kernel specification that will be available in H2O Notebook Lab to run as a Kernel.
    """

    def __init__(
        self,
        kernel_image: str,
        kernel_template: str,
        name: str = "",
        display_name: str = "",
        disabled: bool = False,
    ):
        """
        Args:
            kernel_image (str): Resource name of a KernelImage. Format is `workspaces/*/kernelImages/*`.
            kernel_template (str): Resource name of a KernelTemplate. Format is `workspaces/*/kernelTemplates/*`.
            name (str, optional): Resource name of the NotebookKernelSpec.
                Format is `workspaces/*/notebookKernelSpecs/*`.
            display_name (str, optional): Human-readable name of the NotebookKernelSpec.
                Must contain at most 63 characters. Does not have to be unique.
            disabled (bool, optional): Whether spec is disabled.
        """
        self.kernel_image = kernel_image
        self.kernel_template = kernel_template
        self.name = name
        self.display_name = display_name
        self.disabled = disabled

    def get_notebook_kernel_spec_id(self) -> str:
        segments = self.name.split("/")
        if len(segments) != 4:
            return ""

        return segments[3]

    def __repr__(self) -> str:
        return pprint.pformat(self.__dict__)

    def to_api_object(self) -> V1NotebookKernelSpec:
        return V1NotebookKernelSpec(
            display_name=self.display_name,
            kernel_image=self.kernel_image,
            kernel_template=self.kernel_template,
            disabled=self.disabled,
        )

    def to_resource(self) -> RequiredNotebookKernelSpecResource:
        return RequiredNotebookKernelSpecResource(
            display_name=self.display_name,
            kernel_image=self.kernel_image,
            kernel_template=self.kernel_template,
            disabled=self.disabled,
        )


def from_api_object(api_object: V1NotebookKernelSpec) -> NotebookKernelSpec:
    return NotebookKernelSpec(
        name=api_object.name,
        kernel_image=api_object.kernel_image,
        kernel_template=api_object.kernel_template,
        display_name=api_object.display_name,
        disabled=api_object.disabled,
    )
