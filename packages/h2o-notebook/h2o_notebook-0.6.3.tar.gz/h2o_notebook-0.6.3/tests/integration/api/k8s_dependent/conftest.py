import pytest as pytest

from h2o_notebook.clients.base.workspace import DEFAULT_WORKSPACE
from h2o_notebook.clients.base.workspace import GLOBAL_WORKSPACE
from h2o_notebook.clients.kernel.kernel import Kernel
from h2o_notebook.clients.kernel_image.client import KernelImageClient
from h2o_notebook.clients.kernel_image.kernel_image import KernelImage
from h2o_notebook.clients.kernel_image.type import KernelImageType
from h2o_notebook.clients.kernel_template.client import KernelTemplateClient
from h2o_notebook.clients.kernel_template.kernel_template import KernelTemplate


@pytest.fixture(scope="session")
def kernel_template_session(kernel_template_client_user: KernelTemplateClient, kernel_client_super_admin):
    kernel_template = kernel_template_client_user.create_kernel_template(
        parent=DEFAULT_WORKSPACE,
        kernel_template=KernelTemplate(
            milli_cpu_limit=200,
            gpu=1,
            memory_bytes_limit="1000",
            storage_bytes="1Gi",
            max_idle_duration="600s",
        ),
        kernel_template_id="kt-session1",
    )
    yield kernel_template
    kernel_client_super_admin.wait_all_kernels_deleted(parent=DEFAULT_WORKSPACE)
    kernel_template_client_user.delete_kernel_template(name=kernel_template.name)


@pytest.fixture(scope="session")
def kernel_image_session(kernel_image_client_super_admin: KernelImageClient, kernel_client_super_admin):
    kernel_image = kernel_image_client_super_admin.create_kernel_image(
        parent=GLOBAL_WORKSPACE,
        kernel_image=KernelImage(
            kernel_image_type=KernelImageType.TYPE_PYTHON,
            image="something",
        ),
        kernel_image_id="img-session1",
    )

    yield kernel_image
    kernel_client_super_admin.wait_all_kernels_deleted(parent=DEFAULT_WORKSPACE)
    kernel_image_client_super_admin.delete_kernel_image(name=kernel_image.name)


@pytest.fixture(scope="function")
def kernel_user(kernel_client_user, kernel_template_session, kernel_image_session):
    k = kernel_client_user.create_kernel(
        parent=DEFAULT_WORKSPACE,
        kernel=Kernel(
            kernel_image=kernel_image_session.name,
            kernel_template=kernel_template_session.name,
        ),
    )
    name = k.name
    yield k
    kernel_client_user.delete_kernel(name=name)


@pytest.fixture(scope="function")
def kernel_super_admin(kernel_client_super_admin, kernel_template_session, kernel_image_session):
    k = kernel_client_super_admin.create_kernel(
        parent=DEFAULT_WORKSPACE,
        kernel=Kernel(
            kernel_image=kernel_image_session.name,
            kernel_template=kernel_template_session.name,
        ),
    )
    name = k.name
    yield k
    kernel_client_super_admin.delete_kernel(name=name)


@pytest.fixture(scope="function")
def delete_all_kernels_after(kernel_client_super_admin):
    yield
    kernel_client_super_admin.delete_all_kernels(parent=DEFAULT_WORKSPACE)
