import pprint
from typing import Dict

from h2o_notebook.clients.base.workspace import GLOBAL_WORKSPACE
from h2o_notebook.clients.convert.duration_convertor import duration_to_seconds
from h2o_notebook.clients.convert.quantity_convertor import quantity_to_number_str


class KernelTemplateConfig:
    """KernelTemplateConfig object used as input for apply method."""

    def __init__(
        self,
        kernel_template_id: str,
        gpu: int,
        memory_bytes_limit: str,
        max_idle_duration: str,
        environmental_variables: Dict[str, str] = None,
        yaml_pod_template_spec: str = "",
        gpu_resource: str = "",
        milli_cpu_request: int = 0,
        milli_cpu_limit: int = 0,
        memory_bytes_request: str = "0",
        storage_bytes: str = "0",
        storage_class_name: str = "",
        disabled: bool = False,
        workspace_id: str = "",
    ):
        self.kernel_template_id = kernel_template_id
        self.milli_cpu_limit = milli_cpu_limit
        self.gpu = gpu
        self.memory_bytes_limit = quantity_to_number_str(memory_bytes_limit)
        self.max_idle_duration = duration_to_seconds(max_idle_duration)
        self.environmental_variables = environmental_variables
        self.yaml_pod_template_spec = yaml_pod_template_spec
        self.gpu_resource = gpu_resource
        self.milli_cpu_request = milli_cpu_request
        self.memory_bytes_request = quantity_to_number_str(memory_bytes_request)
        self.storage_bytes = quantity_to_number_str(storage_bytes)
        self.storage_class_name = storage_class_name
        self.disabled = disabled
        self.workspace_id = workspace_id

    def get_name(self):
        return f"{GLOBAL_WORKSPACE}/kernelTemplates/{self.kernel_template_id}"

    def __repr__(self) -> str:
        return pprint.pformat(self.__dict__)
