import http

import pytest

from h2o_notebook.clients.base.workspace import DEFAULT_WORKSPACE
from h2o_notebook.clients.base.workspace import GLOBAL_WORKSPACE
from h2o_notebook.clients.kernel_template.kernel_template import KernelTemplate
from h2o_notebook.exception import CustomApiException


def test_delete_kernel_template_super_admin(
    kernel_template_client_user,
    kernel_template_client_super_admin,
    delete_all_kernel_templates_after,
):
    # When
    kernel_template_client_super_admin.create_kernel_template(
        parent=GLOBAL_WORKSPACE,
        kernel_template=KernelTemplate(
            milli_cpu_limit=200,
            gpu=1,
            memory_bytes_limit="1000",
            max_idle_duration="600s",
        ),
        kernel_template_id="kernel-template-super-admin",
    )
    kernel_template_client_user.create_kernel_template(
        parent=DEFAULT_WORKSPACE,
        kernel_template=KernelTemplate(
            milli_cpu_limit=200,
            gpu=1,
            memory_bytes_limit="1000",
            max_idle_duration="600s",
        ),
        kernel_template_id="kernel-template-user",
    )

    # Then

    # SuperAdmin can delete its own KernelTemplate.
    kernel_template_client_super_admin.delete_kernel_template(
        name=f"{GLOBAL_WORKSPACE}/kernelTemplates/kernel-template-super-admin",
    )
    # Check that deleted KernelTemplate no longer exists.
    with pytest.raises(CustomApiException) as exc:
        kernel_template_client_super_admin.get_kernel_template(
            name=f"{GLOBAL_WORKSPACE}/kernelTemplates/kernel-template-super-admin",
        )
    assert exc.value.status == http.HTTPStatus.NOT_FOUND

    # SuperAdmin tries to delete non-existing KernelTemplate.
    with pytest.raises(CustomApiException) as exc:
        kernel_template_client_super_admin.delete_kernel_template(
            name=f"{GLOBAL_WORKSPACE}/kernelTemplates/kernel-template-super-admin",
        )
    assert exc.value.status == http.HTTPStatus.NOT_FOUND

    # SuperAdmin can delete someone else's existing KernelTemplate.
    kernel_template_client_super_admin.delete_kernel_template(
        name=f"{DEFAULT_WORKSPACE}/kernelTemplates/kernel-template-user",
    )
    # Check that deleted KernelTemplate no longer exists.
    with pytest.raises(CustomApiException) as exc:
        kernel_template_client_super_admin.get_kernel_template(
            name=f"{DEFAULT_WORKSPACE}/kernelTemplates/kernel-template-user",
        )
    assert exc.value.status == http.HTTPStatus.NOT_FOUND


def test_delete_kernel_template_user(
    kernel_template_client_user,
    kernel_template_client_super_admin,
    delete_all_kernel_templates_after,
):
    # When
    kernel_template_client_super_admin.create_kernel_template(
        parent=DEFAULT_WORKSPACE,
        kernel_template=KernelTemplate(
            milli_cpu_limit=200,
            gpu=1,
            memory_bytes_limit="1000",
            max_idle_duration="600s",
        ),
        kernel_template_id="kernel-template-super-admin",
    )
    kernel_template_client_user.create_kernel_template(
        parent=DEFAULT_WORKSPACE,
        kernel_template=KernelTemplate(
            milli_cpu_limit=200,
            gpu=1,
            memory_bytes_limit="1000",
            max_idle_duration="600s",
        ),
        kernel_template_id="kernel-template-user",
    )

    # Then

    # User can delete its own KernelTemplate.
    kernel_template_client_user.delete_kernel_template(
        name=f"{DEFAULT_WORKSPACE}/kernelTemplates/kernel-template-user",
    )
    # Check that user cannot Get the deleted KernelTemplate.
    # User should get 403 (not 404).
    with pytest.raises(CustomApiException) as exc:
        kernel_template_client_user.get_kernel_template(
            name=f"{DEFAULT_WORKSPACE}/kernelTemplates/kernel-template-user",
        )
    assert exc.value.status == http.HTTPStatus.FORBIDDEN

    # User tries to delete non-existing KernelTemplate.
    # User should get 403 (not 404).
    with pytest.raises(CustomApiException) as exc:
        kernel_template_client_user.delete_kernel_template(
            name=f"{DEFAULT_WORKSPACE}/kernelTemplates/kernel-template-user",
        )
    assert exc.value.status == http.HTTPStatus.FORBIDDEN

    # User cannot delete someone else's existing KernelTemplate
    with pytest.raises(CustomApiException) as exc:
        kernel_template_client_user.delete_kernel_template(
            name=f"{DEFAULT_WORKSPACE}/kernelTemplates/kernel-template-super-admin",
        )
    assert exc.value.status == http.HTTPStatus.FORBIDDEN
