import base64
from typing import List

import pytest

from h2o_notebook.clients.kernel.kernel import Kernel
from h2o_notebook.clients.kernel_task.client import KernelTaskClient
from h2o_notebook.clients.kernel_task.kernel_task import KernelTask
from h2o_notebook.clients.kernel_task_output.kernel_task_output import AttachmentData
from tests.integration.e2e.helper import PNG_MAGIC_NUMBER


@pytest.mark.timeout(900)
def test_kernel_task_output(
    kernel_python_user: Kernel,
    kernel_task_client_user: KernelTaskClient,
):
    t = kernel_task_client_user.create_kernel_task(
        parent=kernel_python_user.name,
        kernel_task=KernelTask(
            code=
            """
            import matplotlib.pyplot as plt
            import sys
            print("Hello World", flush=True)
            x = [1, 2]
            y = [2, 1]
            plt.bar(x, y)
            plt.show()
            print("fatal error", file=sys.stderr, flush=True)
            print("Goodbye World", flush=True)
            print("another fatal error", file=sys.stderr, flush=True)
            """,
        ),
    )

    kernel_task_client_user.wait_task_completed(name=t.name)

    # Then
    output = kernel_task_client_user.get_kernel_task_output(
        kernel_task_name=t.name,
    )

    assert output.stdout == "Hello World\nGoodbye World\n"
    assert output.stderr == "fatal error\nanother fatal error\n"

    actual_data = output.attachments[0].data
    assert len(actual_data) == 2

    # The attachment data order is undefined.
    # For testing purposes sort this list by mime_type.
    sorted_actual_data = sort_by_mime_type(actual_data)

    assert sorted_actual_data[0].mime_type == "image/png"
    image_data = sorted_actual_data[0].data
    # Check that image data starts with PNG magic number (that the generated content is PNG)
    decoded_image_data = base64.b64decode(image_data)
    assert decoded_image_data.startswith(PNG_MAGIC_NUMBER)

    assert sorted_actual_data[1].mime_type == "text/plain"
    text_data = sorted_actual_data[1].data
    expected_text_data = "<Figure size 640x480 with 1 Axes>".encode()
    assert expected_text_data == text_data


def sort_by_mime_type(data_list: List[AttachmentData]) -> List[AttachmentData]:
    return sorted(data_list, key=lambda attachment_data: attachment_data.mime_type)
