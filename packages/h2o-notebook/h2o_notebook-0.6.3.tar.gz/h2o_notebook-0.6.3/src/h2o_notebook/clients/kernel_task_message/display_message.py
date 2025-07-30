import base64
from typing import Dict

from h2o_notebook.gen.model.kernel_task_message_display_message import (
    KernelTaskMessageDisplayMessage,
)


class DisplayMessage:
    """
    Additional metadata to display data.
    """

    def __init__(self, display_data: Dict[str, bytes] = None):
        if display_data is None:
            display_data = {}

        self.display_message_data = display_data


def from_display_message_api_object(api_object: KernelTaskMessageDisplayMessage) -> DisplayMessage:
    # Values in the API display_data map are bytes in the form of a base64-encoded string.
    # We want to decode these strings to bytes and store the map with original bytes values.

    display_data: Dict[str, bytes] = {}
    for mime_type, data_str in api_object.display_data.items():
        display_data[mime_type] = base64.b64decode(data_str)

    return DisplayMessage(display_data=display_data)
