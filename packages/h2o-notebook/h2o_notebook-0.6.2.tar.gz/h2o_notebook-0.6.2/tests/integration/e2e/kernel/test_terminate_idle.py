import time

import pytest

from h2o_notebook.clients.kernel.client import KernelClient
from h2o_notebook.clients.kernel.kernel import Kernel
from h2o_notebook.clients.kernel.state import KernelState
from h2o_notebook.clients.kernel_task.client import KernelTaskClient
from tests.integration.e2e.helper import create_instant_task
from tests.integration.e2e.helper import create_long_task


def await_terminating(kernel: Kernel, kernel_client: KernelClient):
    while kernel.state not in [KernelState.STATE_TERMINATING, KernelState.STATE_TERMINATED]:
        time.sleep(3)
        kernel = kernel_client.get_kernel(name=kernel.name)


@pytest.mark.timeout(600)
def test_kernel_terminate_cancelled_tasks(
    kernel_client_user: KernelClient,
    kernel_task_client_user: KernelTaskClient,
    kernel_python_user_low_idle_limit: Kernel,
    kernel_python_user_low_idle_limit2: Kernel,
):
    k1 = kernel_python_user_low_idle_limit
    k2 = kernel_python_user_low_idle_limit2

    # Run an instant task on the first kernel.
    t1 = create_instant_task(kernel_task_client_user, kernel=k1, kernel_task_id="terminate-cancel-1")

    # Run a long task on the second kernel.
    create_long_task(kernel_task_client_user, kernel=k2, kernel_task_id="terminate-cancel-2")

    # Await the instant task to complete.
    kernel_task_client_user.wait_task_completed(name=t1.name)

    # Await the kernel to start terminating.
    await_terminating(k1, kernel_client_user)

    k_idle_updated = kernel_client_user.get_kernel(name=k1.name)
    k_busy_updated = kernel_client_user.get_kernel(name=k2.name)

    assert k_idle_updated.state in [KernelState.STATE_TERMINATING, KernelState.STATE_TERMINATED]
    assert k_busy_updated.state == KernelState.STATE_RUNNING_BUSY
