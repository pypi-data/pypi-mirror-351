import time

from h2o_notebook.clients.kernel.kernel import Kernel
from h2o_notebook.clients.kernel_task.client import KernelTaskClient
from h2o_notebook.clients.kernel_task.kernel_task import KernelTask
from h2o_notebook.clients.kernel_task.state import KernelTaskState

# PNG magic number in bytes
PNG_MAGIC_NUMBER = b'\x89PNG\r\n\x1a\n'


def create_long_task(kernel_task_client_user: KernelTaskClient, kernel: Kernel, kernel_task_id: str = ""):
    return kernel_task_client_user.create_kernel_task(
        parent=kernel.name,
        kernel_task=KernelTask(
            code="""
            import time
            time.sleep(600)
            """,
        ),
        kernel_task_id=kernel_task_id,
    )


def create_instant_task(kernel_task_client_user: KernelTaskClient, kernel: Kernel, kernel_task_id: str = ""):
    return kernel_task_client_user.create_kernel_task(
        parent=kernel.name,
        kernel_task=KernelTask(
            code="""
            print('Hello world!')
            """,
        ),
        kernel_task_id=kernel_task_id,
    )


def wait_task_executing(
    kernel_task_client_user: KernelTaskClient,
    kernel_task: KernelTask,
):
    while True:
        task = kernel_task_client_user.get_kernel_task(name=kernel_task.name)
        if task.state == KernelTaskState.STATE_EXECUTING:
            return task
        if task.state == KernelTaskState.STATE_QUEUED:
            time.sleep(2)
        else:
            raise Exception(f"Task is in unexpected state: {task.state}")
