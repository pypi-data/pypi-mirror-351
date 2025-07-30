from typing import Dict

from h2o_notebook.clients.convert.duration_convertor import duration_to_seconds
from h2o_notebook.clients.convert.duration_convertor import seconds_to_duration
from h2o_notebook.clients.convert.quantity_convertor import number_str_to_quantity
from h2o_notebook.clients.convert.quantity_convertor import quantity_to_number_str
from h2o_notebook.gen.model.v1_kernel_template_info import V1KernelTemplateInfo


class KernelTemplateInfo:
    """
    KernelTemplateInfo contains data from the KernelTemplate that is used to create a Kernel.
    The original KernelTemplate might be deleted during the lifetime of the Kernel.
    """

    def __init__(
        self,
        milli_cpu_request: int = 0,
        milli_cpu_limit: int = 0,
        gpu_resource: str = "",
        gpu: int = 0,
        memory_bytes_request: str = "0",
        memory_bytes_limit: str = "0",
        storage_bytes: str = "0",
        storage_class_name: str = "",
        yaml_pod_template_spec: str = "",
        max_idle_duration: str = "0s",
        template_environmental_variables: Dict[str, str] = None,
    ):
        if template_environmental_variables is None:
            template_environmental_variables = {}

        self.milli_cpu_request = milli_cpu_request
        self.milli_cpu_limit = milli_cpu_limit
        self.gpu_resource = gpu_resource
        self.gpu = gpu
        self.memory_bytes_request = memory_bytes_request
        self.memory_bytes_limit = memory_bytes_limit
        self.storage_bytes = storage_bytes
        self.storage_class_name = storage_class_name
        self.yaml_pod_template_spec = yaml_pod_template_spec
        self.max_idle_duration = max_idle_duration
        self.template_environmental_variables = template_environmental_variables

    def to_api_object(self) -> V1KernelTemplateInfo:
        return V1KernelTemplateInfo(
            milli_cpu_request=self.milli_cpu_request,
            milli_cpu_limit=self.milli_cpu_limit,
            gpu_resource=self.gpu_resource,
            gpu=self.gpu,
            memory_bytes_request=quantity_to_number_str(self.memory_bytes_request),
            memory_bytes_limit=quantity_to_number_str(self.memory_bytes_limit),
            storage_bytes=quantity_to_number_str(self.storage_bytes),
            storage_class_name=self.storage_class_name,
            yaml_pod_template_spec=self.yaml_pod_template_spec,
            max_idle_duration=duration_to_seconds(self.max_idle_duration),
            template_environmental_variables=self.template_environmental_variables,
        )


def from_api_object(api_object: V1KernelTemplateInfo) -> KernelTemplateInfo:
    return KernelTemplateInfo(
        milli_cpu_request=api_object.milli_cpu_request,
        milli_cpu_limit=api_object.milli_cpu_limit,
        gpu_resource=api_object.gpu_resource,
        gpu=api_object.gpu,
        memory_bytes_request=number_str_to_quantity(api_object.memory_bytes_request),
        memory_bytes_limit=number_str_to_quantity(api_object.memory_bytes_limit),
        storage_bytes=number_str_to_quantity(api_object.storage_bytes),
        storage_class_name=api_object.storage_class_name,
        yaml_pod_template_spec=api_object.yaml_pod_template_spec,
        max_idle_duration=seconds_to_duration(api_object.max_idle_duration),
        template_environmental_variables=api_object.template_environmental_variables,
    )
