import base64

import pytest

from h2o_notebook.clients.kernel.kernel import Kernel
from h2o_notebook.clients.kernel_task.client import KernelTaskClient
from h2o_notebook.clients.kernel_task.kernel_task import KernelTask
from h2o_notebook.clients.kernel_task.state import KernelTaskState
from tests.integration.e2e.helper import PNG_MAGIC_NUMBER


@pytest.mark.timeout(900)
@pytest.mark.parametrize(
    ["code", "error", "error_value"],
    [
        ("printHello world!')", "SyntaxError",
         "unterminated string literal (detected at line 1) (1946539443.py, line 1)"),
        ("""
        b=1
        print(a)
        """, "NameError", "name 'a' is not defined"),
        ("1/0", "ZeroDivisionError", "division by zero"),
    ],
)
def test_kernel_task_error(
    kernel_python_user: Kernel,
    kernel_task_client_user: KernelTaskClient,
    code: str,
    error: str,
    error_value: str,
):
    t = kernel_task_client_user.create_kernel_task(
        parent=kernel_python_user.name,
        kernel_task=KernelTask(
            code=code,
        ),
    )

    completed_kernel_task = kernel_task_client_user.wait_task_completed(name=t.name)

    assert completed_kernel_task.state == KernelTaskState.STATE_COMPLETE_ERROR
    assert completed_kernel_task.error == error
    assert completed_kernel_task.error_value == error_value
    assert completed_kernel_task.traceback != ""
    assert completed_kernel_task.execution_start_time < completed_kernel_task.complete_time


@pytest.mark.timeout(900)
@pytest.mark.parametrize(
    ["code", "stdout"],
    [
        ("print('Hello World!')", "Hello World!\n",),
        ("result = 2 + 2 \nprint(result)", "4\n"),
    ],
)
def test_kernel_task_success_stdout(
    kernel_python_user: Kernel,
    kernel_task_client_user: KernelTaskClient,
    code: str,
    stdout: str,
):
    t = kernel_task_client_user.create_kernel_task(
        parent=kernel_python_user.name,
        kernel_task=KernelTask(
            code=code,
        ),
    )

    completed_kernel_task = kernel_task_client_user.wait_task_completed(name=t.name)

    assert completed_kernel_task.state == KernelTaskState.STATE_COMPLETE_SUCCESS
    assert completed_kernel_task.error == ""
    assert completed_kernel_task.error_value == ""
    assert completed_kernel_task.traceback == ""
    assert completed_kernel_task.execution_start_time < completed_kernel_task.complete_time

    messages = kernel_task_client_user.list_all_kernel_task_messages(
        kernel_task_name=t.name,
    )

    assert len(messages) == 1
    message = messages[0]

    assert message.std_out == stdout
    assert message.std_err is None
    assert message.display_message is None


@pytest.mark.timeout(900)
def test_kernel_task_success_display_data(
    kernel_python_user: Kernel,
    kernel_task_client_user: KernelTaskClient,
):
    t = kernel_task_client_user.create_kernel_task(
        parent=kernel_python_user.name,
        kernel_task=KernelTask(
            code=
            """
            import matplotlib.pyplot as plt
            x = [1, 2]
            y = [2, 1]
            plt.bar(x, y)
            plt.show()
            """,
        ),
    )

    completed_kernel_task = kernel_task_client_user.wait_task_completed(name=t.name)

    # Then
    assert completed_kernel_task.state == KernelTaskState.STATE_COMPLETE_SUCCESS
    assert completed_kernel_task.error == ""
    assert completed_kernel_task.error_value == ""
    assert completed_kernel_task.traceback == ""
    assert completed_kernel_task.execution_start_time < completed_kernel_task.complete_time

    messages = kernel_task_client_user.list_all_kernel_task_messages(
        kernel_task_name=t.name,
    )

    assert len(messages) == 1
    image_message = messages[0]

    # The actual message that we want to test in this test case.
    assert image_message.std_out is None
    assert image_message.std_err is None
    assert image_message.display_message is not None

    assert 'text/plain' in image_message.display_message.display_message_data
    text_data = image_message.display_message.display_message_data['text/plain']
    expected_text_data = "<Figure size 640x480 with 1 Axes>".encode()
    assert expected_text_data == text_data

    assert 'image/png' in image_message.display_message.display_message_data
    image_data = image_message.display_message.display_message_data['image/png']
    # Check that image data starts with PNG magic number (that the generated content is PNG)
    decoded_image_data = base64.b64decode(image_data)
    assert decoded_image_data.startswith(PNG_MAGIC_NUMBER)
