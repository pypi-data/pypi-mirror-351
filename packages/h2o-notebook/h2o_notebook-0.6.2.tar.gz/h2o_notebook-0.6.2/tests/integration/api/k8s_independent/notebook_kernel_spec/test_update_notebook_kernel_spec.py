import http
import json

import pytest

from h2o_notebook.clients.base.workspace import GLOBAL_WORKSPACE
from h2o_notebook.clients.notebook_kernel_spec.client import NotebookKernelSpecClient
from h2o_notebook.clients.notebook_kernel_spec.notebook_kernel_spec import (
    NotebookKernelSpec,
)
from h2o_notebook.exception import CustomApiException


def test_update_notebook_kernel_spec(
    notebook_kernel_spec_client_super_admin: NotebookKernelSpecClient,
    notebook_kernel_spec: NotebookKernelSpec,
    kernel_image2,
    kernel_template2,
    delete_all_notebook_kernel_specs_after,
):
    notebook_kernel_spec.display_name = "new-name"
    notebook_kernel_spec.kernel_image = kernel_image2.name
    notebook_kernel_spec.kernel_template = kernel_template2.name
    notebook_kernel_spec.disabled = True

    updated = notebook_kernel_spec_client_super_admin.update_notebook_kernel_spec(
        notebook_kernel_spec=notebook_kernel_spec,
    )

    assert updated.display_name == "new-name"
    assert updated.kernel_image == kernel_image2.name
    assert updated.kernel_template == kernel_template2.name
    assert updated.disabled is True

    updated.display_name = "new-name-2"
    updated.kernel_image = "some-kernel-image"
    updated.kernel_template = "some-kernel-template"
    updated.disabled = False

    updated_again = notebook_kernel_spec_client_super_admin.update_notebook_kernel_spec(
        notebook_kernel_spec=updated,
        update_mask="display_name,disabled",
    )

    assert updated_again.display_name == "new-name-2"
    assert updated_again.kernel_image == kernel_image2.name
    assert updated_again.kernel_template == kernel_template2.name
    assert updated_again.disabled is False


def test_update_notebook_kernel_spec_not_found(
    notebook_kernel_spec_client_super_admin: NotebookKernelSpecClient,
    notebook_kernel_spec: NotebookKernelSpec,
    delete_all_notebook_kernel_specs_after,
):
    notebook_kernel_spec.name = f"{GLOBAL_WORKSPACE}/notebookKernelSpecs/whatever"
    with pytest.raises(CustomApiException) as exc:
        notebook_kernel_spec_client_super_admin.update_notebook_kernel_spec(
            notebook_kernel_spec=notebook_kernel_spec,
        )
    assert exc.value.status == http.HTTPStatus.NOT_FOUND


def test_update_notebook_kernel_spec_client_validation(
    notebook_kernel_spec_client_super_admin: NotebookKernelSpecClient,
    notebook_kernel_spec: NotebookKernelSpec,
    delete_all_notebook_kernel_specs_after,
):
    notebook_kernel_spec.kernel_image = ""

    with pytest.raises(CustomApiException) as exc:
        notebook_kernel_spec_client_super_admin.update_notebook_kernel_spec(
            notebook_kernel_spec=notebook_kernel_spec,
        )
    assert exc.value.status == http.HTTPStatus.BAD_REQUEST
    assert 'validation error: invalid KernelImage name' in json.loads(exc.value.body)["message"]


def test_update_notebook_kernel_spec_forbidden(
    notebook_kernel_spec_client_user: NotebookKernelSpecClient,
    notebook_kernel_spec: NotebookKernelSpec,
    delete_all_notebook_kernel_specs_after,
):
    with pytest.raises(CustomApiException) as exc:
        notebook_kernel_spec_client_user.update_notebook_kernel_spec(
            notebook_kernel_spec=notebook_kernel_spec,
        )
    assert exc.value.status == http.HTTPStatus.FORBIDDEN
