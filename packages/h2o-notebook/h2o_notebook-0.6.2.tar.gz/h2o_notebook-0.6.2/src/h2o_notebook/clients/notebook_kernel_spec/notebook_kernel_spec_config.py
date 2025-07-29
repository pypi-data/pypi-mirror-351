import pprint


class NotebookKernelSpecConfig:
    """NotebookKernelSpecConfig object used as input for apply method."""

    def __init__(
        self,
        notebook_kernel_spec_id: str,
        kernel_image: str,
        kernel_template: str,
        display_name: str = "",
        disabled: bool = False,
    ):
        """
        Arguments are same as in NotebookKernelSpec resource.
        """
        self.notebook_kernel_spec_id = notebook_kernel_spec_id
        self.kernel_image = kernel_image
        self.kernel_template = kernel_template
        self.display_name = display_name
        self.disabled = disabled

    def __repr__(self) -> str:
        return pprint.pformat(self.__dict__)
