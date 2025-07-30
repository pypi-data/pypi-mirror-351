import pytest

from h2o_notebook.clients.kernel.client import KernelClient
from h2o_notebook.clients.kernel.kernel import Kernel
from h2o_notebook.clients.kernel.state import KernelState
from h2o_notebook.clients.kernel_task.client import KernelTaskClient
from h2o_notebook.clients.kernel_task.kernel_task import KernelTask


@pytest.mark.timeout(600)
def test_kernel_failed(
    kernel_python_user_low_memory_limit: Kernel,
    kernel_client_user: KernelClient,
    kernel_task_client_user: KernelTaskClient,
):
    k = kernel_python_user_low_memory_limit
    kernel_task = kernel_task_client_user.create_kernel_task(
        parent=k.name,
        kernel_task=KernelTask(
            code="""
            import time
            try:
                memory_hog = []
                while True:
                    memory_hog.append(' ' * 10**6)  # Add 1MB at a time
                    time.sleep(0.1)  # Sleep a little to slow down the allocation
            except MemoryError:
                print("MemoryError: Out of memory!")
            """,
        ),
        kernel_task_id="failed-1",
    )
    kernel_task_client_user.wait_task_completed(name=kernel_task.name)
    k = kernel_client_user.get_kernel(name=k.name)

    assert k.state == KernelState.STATE_TERMINATING
    assert k.failure_reason == "container kernel failed: OOMKilled: "
