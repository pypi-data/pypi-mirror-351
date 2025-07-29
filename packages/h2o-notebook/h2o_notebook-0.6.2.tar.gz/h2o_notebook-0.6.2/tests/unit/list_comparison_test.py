from collections import Counter
from typing import List

from h2o_notebook.clients.kernel_task_output.kernel_task_output import AttachmentData


def test_attachment_data_comparison():
    list_1: List[AttachmentData] = [
        AttachmentData(mime_type="image/png", data="whatever".encode()),
        AttachmentData(mime_type="text/plain", data="<Figure size 640x480 with 1 Axes>".encode()),
    ]

    list_2: List[AttachmentData] = [
        AttachmentData(mime_type="image/png", data="whatever".encode()),
        AttachmentData(mime_type="text/plain", data="<Figure size 640x480 with 1 Axes>".encode()),
    ]

    list_3: List[AttachmentData] = [
        AttachmentData(mime_type="text/plain", data="<Figure size 640x480 with 1 Axes>".encode()),
        AttachmentData(mime_type="image/png", data="whatever".encode()),
    ]

    # Order matters
    assert list_1 == list_2
    assert list_1 != list_3

    # Order does not matter
    assert Counter(list_1) == Counter(list_2)
    assert Counter(list_1) == Counter(list_3)
