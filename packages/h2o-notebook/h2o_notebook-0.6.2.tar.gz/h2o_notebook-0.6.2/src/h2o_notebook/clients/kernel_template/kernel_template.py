import pprint
from datetime import datetime
from typing import Dict
from typing import Optional

from h2o_notebook.clients.convert.duration_convertor import duration_to_seconds
from h2o_notebook.clients.convert.duration_convertor import seconds_to_duration
from h2o_notebook.clients.convert.quantity_convertor import number_str_to_quantity
from h2o_notebook.clients.convert.quantity_convertor import quantity_to_number_str
from h2o_notebook.gen.model.v1_kernel_template import V1KernelTemplate


class KernelTemplate:
    def __init__(
        self,
        gpu: int,
        memory_bytes_limit: str,
        max_idle_duration: str,
        name: str = "",
        environmental_variables: Dict[str, str] = None,
        yaml_pod_template_spec: str = "",
        gpu_resource: str = "",
        milli_cpu_request: int = 0,
        milli_cpu_limit: int = 0,
        memory_bytes_request: str = "0",
        storage_bytes: str = "0",
        storage_class_name: str = "",
        disabled: bool = False,
        create_time: Optional[datetime] = None,
        update_time: Optional[datetime] = None,
    ):
        """
        Args:
            gpu (int): The number of GPUs the KernelTemplate is allowed to use.
            memory_bytes_limit (str): The maximum amount of memory the KernelTemplate is allowed to use.
            max_idle_duration (str): The maximum amount of time the KernelTemplate is allowed to be idle.
                Must be specified as a number with `s` suffix. Example `3600s`.
            name (str, optional): Resource name of the KernelTemplate. Format is `workspaces/*/kernelTemplates/*`.
            milli_cpu_limit (int, optional): The maximum amount of CPU the KernelTemplate is allowed to use.
            environmental_variables (Dict[str, str], optional): A set of key-value pairs that are passed
                to the KernelTemplate as environment variables.
            yaml_pod_template_spec (str, optional): The YAML pod template spec for the KernelTemplate.
            gpu_resource (str, optional): The name of the GPU resource the KernelTemplate is allowed to use.
                If not specified, a default value will be used.
            milli_cpu_request (int, optional): The minimum amount of CPU the KernelTemplate is allowed to use.
                If not specified, milli_cpu_limit value will be used.
            memory_bytes_request (str, optional): The minimum amount of memory the KernelTemplate is allowed to use.
                If not specified, memory_bytes_limit value will be used.
            storage_bytes (str, optional): The amount of external ephemeral storage that will be mounted
                to the /home/jovyan/workspace directory of the Kernel. If not specified, node disk will be used.
            storage_class_name (str, optional): The name of the Kubernetes storage class that will be used to provision
                the external ephemeral storage. If not specified, the default Kubernetes storage class will be used.
            disabled (bool, optional): Whether template is disabled.
            create_time (str, datetime): Time when the KernelTemplate was created.
            update_time (str, datetime): Time when the KernelTemplate was last updated.
        """
        if environmental_variables is None:
            environmental_variables = {}

        self.gpu = gpu
        self.memory_bytes_limit = memory_bytes_limit
        self.max_idle_duration = max_idle_duration
        self.name = name
        self.environmental_variables = environmental_variables
        self.yaml_pod_template_spec = yaml_pod_template_spec
        self.gpu_resource = gpu_resource
        self.milli_cpu_request = milli_cpu_request
        self.milli_cpu_limit = milli_cpu_limit
        self.memory_bytes_request = memory_bytes_request
        self.storage_bytes = storage_bytes
        self.storage_class_name = storage_class_name
        self.disabled = disabled
        self.create_time = create_time
        self.update_time = update_time

    def get_kernel_template_id(self) -> str:
        segments = self.name.split("/")
        if len(segments) != 4:
            return ""

        return segments[3]

    def __repr__(self) -> str:
        return pprint.pformat(self.__dict__)

    def to_api_object(self) -> V1KernelTemplate:
        return V1KernelTemplate(
            gpu=self.gpu,
            memory_bytes_limit=quantity_to_number_str(self.memory_bytes_limit),
            max_idle_duration=duration_to_seconds(self.max_idle_duration),
            environmental_variables=self.environmental_variables,
            yaml_pod_template_spec=self.yaml_pod_template_spec,
            gpu_resource=self.gpu_resource,
            milli_cpu_request=self.milli_cpu_request,
            milli_cpu_limit=self.milli_cpu_limit,
            memory_bytes_request=quantity_to_number_str(self.memory_bytes_request),
            storage_bytes=quantity_to_number_str(self.storage_bytes),
            storage_class_name=self.storage_class_name,
            disabled=self.disabled,
        )


def from_api_object(api_object: V1KernelTemplate) -> KernelTemplate:
    return KernelTemplate(
        gpu=api_object.gpu,
        memory_bytes_limit=number_str_to_quantity(api_object.memory_bytes_limit),
        max_idle_duration=seconds_to_duration(api_object.max_idle_duration),
        name=api_object.name,
        environmental_variables=api_object.environmental_variables,
        yaml_pod_template_spec=api_object.yaml_pod_template_spec,
        gpu_resource=api_object.gpu_resource,
        milli_cpu_request=api_object.milli_cpu_request,
        milli_cpu_limit=api_object.milli_cpu_limit,
        memory_bytes_request=number_str_to_quantity(api_object.memory_bytes_request),
        storage_bytes=number_str_to_quantity(api_object.storage_bytes),
        storage_class_name=api_object.storage_class_name,
        disabled=api_object.disabled,
        create_time=api_object.create_time,
        update_time=api_object.update_time,
    )
