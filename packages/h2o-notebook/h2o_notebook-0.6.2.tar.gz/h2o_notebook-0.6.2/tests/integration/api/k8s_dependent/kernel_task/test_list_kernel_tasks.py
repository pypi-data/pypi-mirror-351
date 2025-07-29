import http

import pytest

from h2o_notebook.clients.kernel.kernel import Kernel
from h2o_notebook.clients.kernel_task.client import KernelTaskClient
from h2o_notebook.clients.kernel_task.kernel_task import KernelTask
from h2o_notebook.exception import CustomApiException


@pytest.mark.parametrize(
    ["page_size", "page_token"],
    [
        (-20, ""),
        (0, "non-existing-token"),
    ],
)
def test_list_validation(kernel_task_client_user, kernel_user: Kernel, page_size, page_token):
    with pytest.raises(CustomApiException) as exc:
        kernel_task_client_user.list_kernel_tasks(
            parent=kernel_user.name,
            page_size=page_size,
            page_token=page_token,
        )
    assert exc.value.status == http.HTTPStatus.BAD_REQUEST


def test_list_kernel_tasks_pagination(
    kernel_task_client_user: KernelTaskClient,
    kernel_user: Kernel,
):
    # Test no tasks found.
    page = kernel_task_client_user.list_kernel_tasks(parent=kernel_user.name)
    assert len(page.kernel_tasks) == 0
    assert page.next_page_token == ""

    # Arrange
    create_testing_kernel_tasks(kernel_task_client_user, kernel=kernel_user)

    # Test getting first page.
    page = kernel_task_client_user.list_kernel_tasks(parent=kernel_user.name, page_size=1)
    assert len(page.kernel_tasks) == 1
    assert page.next_page_token != ""

    # Test getting second page.
    page = kernel_task_client_user.list_kernel_tasks(
        parent=kernel_user.name,
        page_size=1,
        page_token=page.next_page_token
    )
    assert len(page.kernel_tasks) == 1
    assert page.next_page_token != ""

    # Test getting last page.
    page = kernel_task_client_user.list_kernel_tasks(
        parent=kernel_user.name,
        page_size=1,
        page_token=page.next_page_token,
    )
    assert len(page.kernel_tasks) == 1
    assert page.next_page_token == ""

    # Test exceeding max page size.
    page = kernel_task_client_user.list_kernel_tasks(
        parent=kernel_user.name,
        page_size=1001,
    )
    assert len(page.kernel_tasks) == 3
    assert page.next_page_token == ""


def test_list_all_kernel_tasks_user(
    kernel_task_client_user: KernelTaskClient,
    kernel_user: Kernel,
):
    # Arrange
    create_testing_kernel_tasks(kernel_task_client_user, kernel=kernel_user)

    # Test basic list_all.
    kernel_tasks = kernel_task_client_user.list_all_kernel_tasks(parent=kernel_user.name)
    assert len(kernel_tasks) == 3


def create_testing_kernel_tasks(kernel_task_client: KernelTaskClient, kernel: Kernel):
    kernel_task_client.create_kernel_task(
        parent=kernel.name,
        kernel_task=KernelTask(
            code="print('Hello world!')",
        ),
        kernel_task_id="task1",
    )
    kernel_task_client.create_kernel_task(
        parent=kernel.name,
        kernel_task=KernelTask(
            code="print('Hello world!')",
        ),
        kernel_task_id="task2",
    )
    kernel_task_client.create_kernel_task(
        parent=kernel.name,
        kernel_task=KernelTask(
            code="print('Hello world!')",
        ),
        kernel_task_id="task3",
    )
