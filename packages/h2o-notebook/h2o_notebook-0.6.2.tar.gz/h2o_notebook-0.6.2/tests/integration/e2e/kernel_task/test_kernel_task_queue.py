import pytest

from h2o_notebook.clients.kernel.kernel import Kernel
from h2o_notebook.clients.kernel_task.client import KernelTaskClient
from tests.integration.e2e.helper import create_long_task
from tests.integration.e2e.helper import wait_task_executing


@pytest.mark.timeout(300)
def test_kernel_task_queue(
    kernel_python_user: Kernel,
    kernel_task_client_user: KernelTaskClient,
):
    t1 = create_long_task(kernel_task_client_user, kernel=kernel_python_user, kernel_task_id="queue-1")

    assert t1.sequence_number == 1
    assert t1.tasks_ahead_count == 0

    t2 = create_long_task(kernel_task_client_user, kernel=kernel_python_user, kernel_task_id="queue-2")
    t3 = create_long_task(kernel_task_client_user, kernel=kernel_python_user, kernel_task_id="queue-3")

    assert t3.sequence_number == 3
    assert t3.tasks_ahead_count == 2

    # Cancel queued task
    kernel_task_client_user.cancel_kernel_task(name=t2.name)
    t3 = kernel_task_client_user.get_kernel_task(name=t3.name)

    assert t3.sequence_number == 3
    assert t3.tasks_ahead_count == 1

    wait_task_executing(kernel_task_client_user, kernel_task=t1)

    # List
    tasks = kernel_task_client_user.list_all_kernel_tasks(parent=kernel_python_user.name)
    assert len(tasks) == 3
    assert tasks[0].sequence_number == 3
    assert tasks[1].sequence_number == 2
    assert tasks[2].sequence_number == 1

    assert tasks[0].tasks_ahead_count == 1
    assert tasks[1].tasks_ahead_count == 0
    assert tasks[2].tasks_ahead_count == 0
