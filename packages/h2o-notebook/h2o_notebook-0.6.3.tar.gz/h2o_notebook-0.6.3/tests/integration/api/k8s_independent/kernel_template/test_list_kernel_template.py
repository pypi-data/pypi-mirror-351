import http

import pytest

from h2o_notebook.clients.base.workspace import DEFAULT_WORKSPACE
from h2o_notebook.clients.base.workspace import GLOBAL_WORKSPACE
from h2o_notebook.clients.kernel_template.client import KernelTemplateClient
from h2o_notebook.clients.kernel_template.kernel_template import KernelTemplate
from h2o_notebook.exception import CustomApiException


@pytest.mark.parametrize(
    ["page_size", "page_token"],
    [
        (-20, ""),
        (0, "non-existing-token"),
    ],
)
def test_list_validation(
    kernel_template_client_super_admin: KernelTemplateClient, page_size, page_token
):
    with pytest.raises(CustomApiException) as exc:
        kernel_template_client_super_admin.list_kernel_templates(
            parent=GLOBAL_WORKSPACE,
            page_size=page_size,
            page_token=page_token,
        )
    assert exc.value.status == http.HTTPStatus.BAD_REQUEST


def test_list_pagination_super_admin(
    delete_all_kernel_templates_after,
    kernel_template_client_super_admin,
):
    # Test no profiles found.
    page = kernel_template_client_super_admin.list_kernel_templates(parent=GLOBAL_WORKSPACE)
    assert len(page.kernel_templates) == 0
    assert page.next_page_token == ""

    # Create 2 kernelTemplates by SuperAdmin
    create_kernel_templates(
        kernel_template_client_super_admin,
        base_id="kernel-template-super-admin",
        cnt=2,
    )
    # Create 1 kernelTemplate by User
    create_kernel_templates(
        kernel_template_client_super_admin,
        base_id="kernel-template-user",
        cnt=1,
    )

    # Test that SuperAdmin pages over all three KernelTemplates.
    assert_list_pagination_three_kernel_templates(
        kernel_template_client=kernel_template_client_super_admin,
    )


def test_list_pagination_user(
    delete_all_kernel_templates_after,
    kernel_template_client_user,
    kernel_template_client_super_admin,
):
    # Test no profiles found.
    page = kernel_template_client_user.list_kernel_templates(parent=DEFAULT_WORKSPACE)
    assert len(page.kernel_templates) == 0
    assert page.next_page_token == ""

    # Create three KernelTemplates by User
    create_kernel_templates(
        kernel_template_client=kernel_template_client_user,
        base_id="kernel-template-user",
        parent=DEFAULT_WORKSPACE,
    )
    # Create 2 KernelTemplates by SuperAdmin
    create_kernel_templates(
        kernel_template_client=kernel_template_client_super_admin,
        base_id="kernel-template-super-admin",
        parent=DEFAULT_WORKSPACE,
        cnt=2,
    )

    # Test that User still pages only over three KernelTemplates.
    assert_list_pagination_three_kernel_templates(
        kernel_template_client=kernel_template_client_user, parent=DEFAULT_WORKSPACE,
    )


def assert_list_pagination_three_kernel_templates(kernel_template_client: KernelTemplateClient, parent=GLOBAL_WORKSPACE):
    # Test getting first page.
    page = kernel_template_client.list_kernel_templates(
        parent=parent,
        page_size=1,
    )
    assert len(page.kernel_templates) == 1
    assert page.next_page_token != ""

    # Test getting second page.
    page = kernel_template_client.list_kernel_templates(
        parent=parent,
        page_size=1,
        page_token=page.next_page_token,
    )
    assert len(page.kernel_templates) == 1
    assert page.next_page_token != ""

    # Test getting last page.
    page = kernel_template_client.list_kernel_templates(
        parent=parent,
        page_size=1,
        page_token=page.next_page_token,
    )
    assert len(page.kernel_templates) == 1
    assert page.next_page_token == ""

    # Test exceeding max page size.
    page = kernel_template_client.list_kernel_templates(
        parent=parent,
        page_size=1001,
    )
    assert len(page.kernel_templates) == 3
    assert page.next_page_token == ""


def test_list_all_super_admin(
    delete_all_kernel_templates_after,
    kernel_template_client_super_admin,
):
    # Arrange
    create_kernel_templates(kernel_template_client=kernel_template_client_super_admin)

    # Test basic list_all.
    kernel_templates = kernel_template_client_super_admin.list_all_kernel_templates(parent=GLOBAL_WORKSPACE)
    assert len(kernel_templates) == 3


def test_list_all_user(
    delete_all_kernel_templates_after,
    kernel_template_client_user,
):
    # Arrange
    create_kernel_templates(kernel_template_client=kernel_template_client_user, parent=DEFAULT_WORKSPACE)

    # Test basic list_all.
    kernel_templates = kernel_template_client_user.list_all_kernel_templates(parent=DEFAULT_WORKSPACE)
    assert len(kernel_templates) == 3


def create_kernel_templates(
    kernel_template_client: KernelTemplateClient,
    base_id: str = "kernel-template",
    parent: str = GLOBAL_WORKSPACE,
    cnt: int = 3,
):
    for i in range(cnt):
        kernel_template_client.create_kernel_template(
            parent=parent,
            kernel_template=KernelTemplate(
                milli_cpu_limit=100,
                gpu=1,
                memory_bytes_limit="1000",
                max_idle_duration="1s",
            ),
            kernel_template_id=f"{base_id}-{i + 1}",
        )


def test_list_auth(
    kernel_template_user,
    kernel_template_super_admin,
    kernel_template_client_user,
    kernel_template_client_super_admin,
):
    # SuperAdmin can list all kernel templates.
    kts = kernel_template_client_super_admin.list_all_kernel_templates(parent=GLOBAL_WORKSPACE)
    assert len(kts) == 1
    assert kts[0].name == f"{GLOBAL_WORKSPACE}/kernelTemplates/kernel-template-super-admin"
    kts = kernel_template_client_super_admin.list_all_kernel_templates(parent=DEFAULT_WORKSPACE)
    assert len(kts) == 1
    assert kts[0].name == f"{DEFAULT_WORKSPACE}/kernelTemplates/kernel-template-user"

    # User can list only its own kernel templates.
    kts = kernel_template_client_user.list_all_kernel_templates(parent=DEFAULT_WORKSPACE)
    assert len(kts) == 1
    assert kts[0].name == f"{DEFAULT_WORKSPACE}/kernelTemplates/kernel-template-user"
