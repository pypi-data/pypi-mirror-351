import pytest

from h2o_notebook.clients.kernel.client import KernelClient
from h2o_notebook.clients.kernel.kernel import Kernel
from h2o_notebook.clients.kernel.state import KernelState
from h2o_notebook.clients.kernel_task.client import KernelTaskClient
from h2o_notebook.clients.kernel_task.kernel_task import KernelTask


@pytest.mark.timeout(600)
def test_kernel_terminate(
        kernel_python_user: Kernel,
        kernel_client_user: KernelClient,
        kernel_task_client_user: KernelTaskClient,
):
    k: Kernel = kernel_python_user
    kernel_task = kernel_task_client_user.create_kernel_task(
        parent=k.name,
        kernel_task=KernelTask(
            code="print('Hello world!')",
        ),
        kernel_task_id="terminate-1",
    )
    kernel_task_client_user.wait_task_completed(name=kernel_task.name)

    k = kernel_client_user.terminate_kernel(name=k.name)

    assert k.state == KernelState.STATE_TERMINATING

    # Test KernelTask available after the Kernel termination
    kt = kernel_task_client_user.list_all_kernel_tasks(parent=k.name)
    assert len(kt) == 1

    # Test noop terminate
    kernel_client_user.terminate_kernel(name=k.name)
