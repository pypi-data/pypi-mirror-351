import http

import pytest

from h2o_notebook.clients.base.workspace import GLOBAL_WORKSPACE
from h2o_notebook.clients.kernel_image.client import KernelImageClient
from h2o_notebook.clients.kernel_image.kernel_image import KernelImage
from h2o_notebook.clients.kernel_image.type import KernelImageType
from h2o_notebook.exception import CustomApiException


@pytest.mark.parametrize(
    ["page_size", "page_token"],
    [
        (-20, ""),
        (0, "non-existing-token"),
    ],
)
def test_list_super_admin_validation(kernel_image_client_super_admin, page_size, page_token):
    with pytest.raises(CustomApiException) as exc:
        kernel_image_client_super_admin.list_kernel_images(
            parent=GLOBAL_WORKSPACE,
            page_size=page_size,
            page_token=page_token,
        )
    assert exc.value.status == http.HTTPStatus.BAD_REQUEST


def test_list_kernel_images_super_admin_pagination(
    delete_all_kernel_images_before_after,
    kernel_image_client_super_admin,
):
    assert_list_kernel_images_pagination(
        kernel_image_client_creator=kernel_image_client_super_admin,
        kernel_image_client_tested=kernel_image_client_super_admin,
    )


def test_list_kernel_images_user_pagination(
    delete_all_kernel_images_after,
    kernel_image_client_super_admin,
    kernel_image_client_user,
):
    assert_list_kernel_images_pagination(
        kernel_image_client_creator=kernel_image_client_super_admin,
        kernel_image_client_tested=kernel_image_client_user,
    )


def assert_list_kernel_images_pagination(
    kernel_image_client_creator: KernelImageClient,
    kernel_image_client_tested: KernelImageClient,
):
    # Test no kernelImages found.
    page = kernel_image_client_tested.list_kernel_images(parent=GLOBAL_WORKSPACE)
    assert len(page.kernel_images) == 0
    assert page.next_page_token == ""

    # Arrange
    create_testing_kernel_images(kernel_image_client_creator=kernel_image_client_creator)

    # Test getting first page.
    page = kernel_image_client_tested.list_kernel_images(
        parent=GLOBAL_WORKSPACE,
        page_size=1,
    )
    assert len(page.kernel_images) == 1
    assert page.next_page_token != ""

    # Test getting second page.
    page = kernel_image_client_tested.list_kernel_images(
        parent=GLOBAL_WORKSPACE,
        page_size=1,
        page_token=page.next_page_token,
    )
    assert len(page.kernel_images) == 1
    assert page.next_page_token != ""

    # Test getting last page.
    page = kernel_image_client_tested.list_kernel_images(
        parent=GLOBAL_WORKSPACE,
        page_size=1,
        page_token=page.next_page_token,
    )
    assert len(page.kernel_images) == 1
    assert page.next_page_token == ""

    # Test exceeding max page size.
    page = kernel_image_client_tested.list_kernel_images(
        parent=GLOBAL_WORKSPACE,
        page_size=1001,
    )
    assert len(page.kernel_images) == 3
    assert page.next_page_token == ""


def test_list_all_kernel_images_super_admin(kernel_image_client_super_admin, delete_all_kernel_images_after):
    # Arrange
    create_testing_kernel_images(kernel_image_client_creator=kernel_image_client_super_admin)

    # Test basic list_all.
    kernel_images = kernel_image_client_super_admin.list_all_kernel_images(
        parent=GLOBAL_WORKSPACE,
    )
    assert len(kernel_images) == 3


def test_list_all_kernel_images_user(
    kernel_image_client_super_admin,
    kernel_image_client_user,
    delete_all_kernel_images_after,
):
    # Arrange
    create_testing_kernel_images(kernel_image_client_creator=kernel_image_client_super_admin)

    # Test basic list_all.
    kernel_images = kernel_image_client_user.list_all_kernel_images(
        parent=GLOBAL_WORKSPACE,
    )
    assert len(kernel_images) == 3


def create_testing_kernel_images(kernel_image_client_creator: KernelImageClient):
    kernel_image_client_creator.create_kernel_image(
        parent=GLOBAL_WORKSPACE,
        kernel_image=KernelImage(
            kernel_image_type=KernelImageType.TYPE_PYTHON,
            image="something1",
        ),
        kernel_image_id="img1",
    )
    kernel_image_client_creator.create_kernel_image(
        parent=GLOBAL_WORKSPACE,
        kernel_image=KernelImage(
            kernel_image_type=KernelImageType.TYPE_PYTHON,
            image="something2",
        ),
        kernel_image_id="img2",
    )
    kernel_image_client_creator.create_kernel_image(
        parent=GLOBAL_WORKSPACE,
        kernel_image=KernelImage(
            kernel_image_type=KernelImageType.TYPE_PYTHON,
            image="something3",
        ),
        kernel_image_id="img3",
    )
