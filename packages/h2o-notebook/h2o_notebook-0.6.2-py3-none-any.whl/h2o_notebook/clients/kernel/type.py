from enum import Enum

from h2o_notebook.gen.model.v1_kernel_type import V1KernelType


class KernelType(Enum):
    TYPE_UNSPECIFIED = "TYPE_UNSPECIFIED"
    TYPE_NOTEBOOK = "TYPE_NOTEBOOK"
    TYPE_HEADLESS = "TYPE_HEADLESS"

    def to_api_object(self) -> V1KernelType:
        return V1KernelType(self.name)


def from_api_object(kernel_type: V1KernelType) -> KernelType:
    return KernelType(str(kernel_type))
