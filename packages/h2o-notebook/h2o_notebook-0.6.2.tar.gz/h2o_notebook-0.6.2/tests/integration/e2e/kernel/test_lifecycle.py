import pytest

from h2o_notebook.clients.base.workspace import DEFAULT_WORKSPACE
from h2o_notebook.clients.base.workspace import GLOBAL_WORKSPACE
from h2o_notebook.clients.kernel.kernel import Kernel
from h2o_notebook.clients.kernel_task.kernel_task import KernelTask
from h2o_notebook.clients.kernel_task.state import KernelTaskState


@pytest.mark.timeout(900)
def test_kernel_lifecycle(
    kernel_client_super_admin,
    kernel_task_client_super_admin,
    delete_all_kernels_after,
):
    kernel = kernel_client_super_admin.create_kernel(
        parent=DEFAULT_WORKSPACE,
        kernel=Kernel(
            kernel_image=f"{GLOBAL_WORKSPACE}/kernelImages/python",
            kernel_template=f"{GLOBAL_WORKSPACE}/kernelTemplates/local",
        ),
        kernel_id="kernel1",
    )

    kernel_task = kernel_task_client_super_admin.create_kernel_task(
        parent=kernel.name,
        kernel_task=KernelTask(
            code="print('Hello world!')",
        ),
        kernel_task_id="kernel-lifecycle-1",
    )

    completed_kernel_task = kernel_task_client_super_admin.wait_task_completed(
        name=kernel_task.name,
    )

    assert completed_kernel_task.state == KernelTaskState.STATE_COMPLETE_SUCCESS

    kernel_client_super_admin.delete_kernel(name=kernel.name)
