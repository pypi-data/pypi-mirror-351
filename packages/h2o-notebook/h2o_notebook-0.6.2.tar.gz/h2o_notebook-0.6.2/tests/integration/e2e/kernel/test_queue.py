import pytest

from h2o_notebook.clients.kernel.client import KernelClient
from h2o_notebook.clients.kernel.kernel import Kernel
from h2o_notebook.clients.kernel.state import KernelState
from h2o_notebook.clients.kernel_task.client import KernelTaskClient
from tests.integration.e2e.helper import create_long_task
from tests.integration.e2e.helper import wait_task_executing


@pytest.mark.timeout(60)
def test_kernel_queue(
    kernel_python_user: Kernel,
    kernel_client_user: KernelClient,
    kernel_task_client_user: KernelTaskClient,
):
    k: Kernel = kernel_python_user

    assert k.current_task == ""
    assert k.current_task_sequence_number == 0
    assert k.task_queue_size == 0

    # Create 3 long-running tasks
    t1 = create_long_task(kernel_task_client_user, kernel=k, kernel_task_id="kernel-queue-1")
    t2 = create_long_task(kernel_task_client_user, kernel=k, kernel_task_id="kernel-queue-2")
    t3 = create_long_task(kernel_task_client_user, kernel=k, kernel_task_id="kernel-queue-3")

    # Wait for the first task to start executing
    wait_task_executing(kernel_task_client_user, kernel_task=t1)

    k = kernel_client_user.get_kernel(name=k.name)

    assert k.state == KernelState.STATE_RUNNING_BUSY
    assert k.current_task == t1.name
    assert k.current_task_sequence_number == t1.sequence_number
    assert k.task_queue_size == 2

    # Cancel the first and second task
    kernel_task_client_user.cancel_kernel_task(name=t1.name)
    kernel_task_client_user.cancel_kernel_task(name=t2.name)

    # Wait for the third task to start executing
    wait_task_executing(kernel_task_client_user, kernel_task=t3)

    k = kernel_client_user.get_kernel(name=k.name)

    assert k.state == KernelState.STATE_RUNNING_BUSY
    assert k.current_task == t3.name
    assert k.current_task_sequence_number == t3.sequence_number
    assert k.task_queue_size == 0
