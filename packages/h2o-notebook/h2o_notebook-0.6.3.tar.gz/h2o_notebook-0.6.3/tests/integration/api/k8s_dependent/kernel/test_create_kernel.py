import http

import pytest

from h2o_notebook.clients.base.workspace import DEFAULT_WORKSPACE
from h2o_notebook.clients.kernel.client import KernelClient
from h2o_notebook.clients.kernel.kernel import Kernel
from h2o_notebook.clients.kernel.state import KernelState
from h2o_notebook.clients.kernel.type import KernelType
from h2o_notebook.clients.kernel_image.kernel_image import KernelImage
from h2o_notebook.clients.kernel_template.kernel_template import KernelTemplate
from h2o_notebook.exception import CustomApiException


def test_create_kernel_default_values(
    kernel_client_user: KernelClient,
    kernel_image_session: KernelImage,
    kernel_template_session: KernelTemplate,
    delete_all_kernels_after,
):
    k = kernel_client_user.create_kernel(
        parent=DEFAULT_WORKSPACE,
        kernel=Kernel(
            kernel_image=kernel_image_session.name,
            kernel_template=kernel_template_session.name,
        ),
    )

    assert k.name.startswith(f"{DEFAULT_WORKSPACE}/kernels/")
    assert k.get_kernel_id() != ""
    assert k.state == KernelState.STATE_STARTING
    assert k.kernel_type == KernelType.TYPE_HEADLESS
    assert k.display_name == ""
    assert k.kernel_image == kernel_image_session.name
    assert k.kernel_template == kernel_template_session.name
    assert k.environmental_variables == {}
    assert k.creator != ""
    assert k.creator_display_name != ""
    assert k.current_task == ""
    assert k.current_task_sequence_number == 0
    assert k.task_queue_size == 0
    assert k.create_time is not None
    assert k.last_activity_time is None
    assert k.notebook_kernel_spec == ""

    assert k.kernel_image_info.image == kernel_image_session.image
    assert k.kernel_image_info.kernel_image_type == kernel_image_session.kernel_image_type

    assert k.kernel_template_info.milli_cpu_limit == kernel_template_session.milli_cpu_limit
    assert k.kernel_template_info.gpu == kernel_template_session.gpu
    assert k.kernel_template_info.memory_bytes_limit == kernel_template_session.memory_bytes_limit
    assert k.kernel_template_info.storage_bytes == kernel_template_session.storage_bytes
    assert k.kernel_template_info.max_idle_duration == kernel_template_session.max_idle_duration
    assert k.kernel_template_info.yaml_pod_template_spec == kernel_template_session.yaml_pod_template_spec
    assert k.kernel_template_info.gpu_resource == kernel_template_session.gpu_resource
    assert k.kernel_template_info.milli_cpu_request == kernel_template_session.milli_cpu_request
    assert k.kernel_template_info.memory_bytes_request == kernel_template_session.memory_bytes_request
    assert k.kernel_template_info.storage_class_name == kernel_template_session.storage_class_name
    assert k.kernel_template_info.template_environmental_variables == kernel_template_session.environmental_variables


def test_create_kernel_full_params(
    kernel_client_user: KernelClient,
    kernel_image_session: KernelImage,
    kernel_template_session: KernelTemplate,
    delete_all_kernels_after,
):
    k = kernel_client_user.create_kernel(
        parent=DEFAULT_WORKSPACE,
        kernel=Kernel(
            kernel_image=kernel_image_session.name,
            kernel_template=kernel_template_session.name,
            display_name="My Kernel",
            environmental_variables={"key": "value"},
        ),
        kernel_id="kernel1",
    )

    assert k.name == f"{DEFAULT_WORKSPACE}/kernels/kernel1"
    assert k.get_kernel_id() == "kernel1"
    assert k.state == KernelState.STATE_STARTING
    assert k.kernel_type == KernelType.TYPE_HEADLESS
    assert k.display_name == "My Kernel"
    assert k.kernel_image == kernel_image_session.name
    assert k.kernel_template == kernel_template_session.name
    assert k.environmental_variables == {"key": "value"}
    assert k.creator != ""
    assert k.creator_display_name != ""
    assert k.current_task == ""
    assert k.current_task_sequence_number == 0
    assert k.task_queue_size == 0
    assert k.create_time is not None
    assert k.last_activity_time is None
    assert k.notebook_kernel_spec == ""


def test_create_kernel_generate_kernel_id(
    kernel_client_user: KernelClient,
    kernel_image_session: KernelImage,
    kernel_template_session: KernelTemplate,
    delete_all_kernels_after
):
    k1 = kernel_client_user.create_kernel(
        parent=DEFAULT_WORKSPACE,
        kernel=Kernel(
            kernel_image=kernel_image_session.name,
            kernel_template=kernel_template_session.name,
        ),
    )

    k2 = kernel_client_user.create_kernel(
        parent=DEFAULT_WORKSPACE,
        kernel=Kernel(
            kernel_image=kernel_image_session.name,
            kernel_template=kernel_template_session.name,
        ),
    )

    assert k1.name != k2.name
    assert k1.get_kernel_id() != k2.get_kernel_id()


def test_create_kernel_already_exists(
    kernel_client_user: KernelClient,
    kernel_image_session: KernelImage,
    kernel_template_session: KernelTemplate,
    delete_all_kernels_after,
):
    k = kernel_client_user.create_kernel(
        parent=DEFAULT_WORKSPACE,
        kernel=Kernel(
            kernel_image=kernel_image_session.name,
            kernel_template=kernel_template_session.name,
        ),
    )

    with pytest.raises(CustomApiException) as exc:
        # Try to create Kernel with the same ID.
        kernel_client_user.create_kernel(
            parent=DEFAULT_WORKSPACE,
            kernel=Kernel(
                kernel_image=kernel_image_session.name,
                kernel_template=kernel_template_session.name,
            ),
            kernel_id=k.get_kernel_id(),
        )

    # grpc AlreadyExists == http Conflict 409
    assert exc.value.status == http.HTTPStatus.CONFLICT
