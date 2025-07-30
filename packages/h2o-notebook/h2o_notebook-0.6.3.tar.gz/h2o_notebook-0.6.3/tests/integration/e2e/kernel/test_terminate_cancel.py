import pytest

from h2o_notebook.clients.kernel.client import KernelClient
from h2o_notebook.clients.kernel.kernel import Kernel
from h2o_notebook.clients.kernel.state import KernelState
from h2o_notebook.clients.kernel_task.client import KernelTaskClient
from h2o_notebook.clients.kernel_task.kernel_task import KernelTask
from h2o_notebook.clients.kernel_task.state import KernelTaskState
from tests.integration.e2e.helper import create_long_task
from tests.integration.e2e.helper import wait_task_executing


@pytest.mark.timeout(600)
def test_kernel_terminate_cancelled_tasks(
    kernel_python_user: Kernel,
    kernel_client_user: KernelClient,
    kernel_task_client_user: KernelTaskClient,
):
    k: Kernel = kernel_python_user
    t1 = kernel_task_client_user.create_kernel_task(
        parent=k.name,
        kernel_task=KernelTask(
            code="print('Hello world!')",
        ),
        kernel_task_id="terminate-cancel-1",
    )
    kernel_task_client_user.wait_task_completed(name=t1.name)

    t2 = create_long_task(kernel_task_client_user, kernel=k, kernel_task_id="terminate-cancel-2")
    t3 = create_long_task(kernel_task_client_user, kernel=k, kernel_task_id="terminate-cancel-3")

    # Wait for the second task to begin executing
    wait_task_executing(kernel_task_client_user, kernel_task=t2)

    k = kernel_client_user.terminate_kernel(name=k.name)

    assert k.state == KernelState.STATE_TERMINATING

    t1 = kernel_task_client_user.get_kernel_task(name=t1.name)
    t2 = kernel_task_client_user.get_kernel_task(name=t2.name)
    t3 = kernel_task_client_user.get_kernel_task(name=t3.name)

    assert t1.state == KernelTaskState.STATE_COMPLETE_SUCCESS
    assert t2.state == KernelTaskState.STATE_CANCELLED
    assert t3.state == KernelTaskState.STATE_CANCELLED
