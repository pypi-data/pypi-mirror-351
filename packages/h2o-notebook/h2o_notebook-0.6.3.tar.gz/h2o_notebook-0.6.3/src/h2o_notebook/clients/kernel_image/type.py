from enum import Enum

from h2o_notebook.gen.model.v1_kernel_image_type import V1KernelImageType


class KernelImageType(Enum):
    TYPE_UNSPECIFIED = "TYPE_UNSPECIFIED"
    TYPE_PYTHON = "TYPE_PYTHON"
    TYPE_R = "TYPE_R"
    TYPE_SPARK_PYTHON = "TYPE_SPARK_PYTHON"
    TYPE_SPARK_R = "TYPE_SPARK_R"

    def to_api_object(self) -> V1KernelImageType:
        return V1KernelImageType(self.name)


def from_api_object(kernel_image_type: V1KernelImageType) -> KernelImageType:
    return KernelImageType(str(kernel_image_type))
