import pytest as pytest

from h2o_notebook.clients.base.workspace import DEFAULT_WORKSPACE
from h2o_notebook.clients.base.workspace import GLOBAL_WORKSPACE
from h2o_notebook.clients.kernel_image.client import KernelImageClient
from h2o_notebook.clients.kernel_image.kernel_image import KernelImage
from h2o_notebook.clients.kernel_image.type import KernelImageType
from h2o_notebook.clients.kernel_template.client import KernelTemplateClient
from h2o_notebook.clients.kernel_template.kernel_template import KernelTemplate
from h2o_notebook.clients.notebook_kernel_spec.client import NotebookKernelSpecClient
from h2o_notebook.clients.notebook_kernel_spec.notebook_kernel_spec import (
    NotebookKernelSpec,
)


@pytest.fixture(scope="function")
def delete_all_kernel_images_after(kernel_image_client_super_admin):
    yield
    kernel_image_client_super_admin.delete_all_kernel_images(parent=GLOBAL_WORKSPACE)


@pytest.fixture(scope="function")
def delete_all_kernel_images_before_after(kernel_image_client_super_admin):
    kernel_image_client_super_admin.delete_all_kernel_images(parent=GLOBAL_WORKSPACE)
    yield
    kernel_image_client_super_admin.delete_all_kernel_images(parent=GLOBAL_WORKSPACE)


@pytest.fixture(scope="function")
def kernel_image_super_admin(kernel_image_client_super_admin):
    ki = kernel_image_client_super_admin.create_kernel_image(
        parent=GLOBAL_WORKSPACE,
        kernel_image=KernelImage(
            kernel_image_type=KernelImageType.TYPE_PYTHON,
            image="something",
        ),
        kernel_image_id="kernel-image-super-admin",
    )
    name = ki.name
    yield ki
    kernel_image_client_super_admin.delete_kernel_image(name=name)


@pytest.fixture(scope="function")
def delete_all_kernel_templates_after(kernel_template_client_super_admin):
    yield
    kernel_template_client_super_admin.delete_all_kernel_templates(
        parent=GLOBAL_WORKSPACE,
    )
    kernel_template_client_super_admin.delete_all_kernel_templates(
        parent=DEFAULT_WORKSPACE,
    )


@pytest.fixture(scope="function")
def kernel_template_super_admin(kernel_template_client_super_admin):
    kt = kernel_template_client_super_admin.create_kernel_template(
        parent=GLOBAL_WORKSPACE,
        kernel_template=KernelTemplate(
            milli_cpu_limit=200,
            milli_cpu_request=200,
            gpu=1,
            memory_bytes_limit="1M",
            memory_bytes_request="1M",
            storage_bytes="1G",
            storage_class_name="standard",
            max_idle_duration="1h",
        ),
        kernel_template_id="kernel-template-super-admin",
    )
    yield kt
    kernel_template_client_super_admin.delete_kernel_template(name=kt.name)


@pytest.fixture(scope="function")
def kernel_template_user(kernel_template_client_user, kernel_template_client_super_admin):
    kt = kernel_template_client_user.create_kernel_template(
        parent=DEFAULT_WORKSPACE,
        kernel_template=KernelTemplate(
            milli_cpu_limit=200,
            milli_cpu_request=200,
            gpu=1,
            memory_bytes_limit="1M",
            memory_bytes_request="1M",
            storage_bytes="1G",
            storage_class_name="standard",
            max_idle_duration="1h",
        ),
        kernel_template_id="kernel-template-user",
    )
    yield kt
    kernel_template_client_super_admin.delete_kernel_template(name=kt.name)


@pytest.fixture(scope="function")
def kernel_image(kernel_image_client_super_admin: KernelImageClient):
    kernel_image = kernel_image_client_super_admin.create_kernel_image(
        parent=GLOBAL_WORKSPACE,
        kernel_image=KernelImage(
            kernel_image_type=KernelImageType.TYPE_PYTHON,
            image="something",
        ),
        kernel_image_id="img1",
    )

    yield kernel_image
    kernel_image_client_super_admin.delete_kernel_image(name=kernel_image.name)


@pytest.fixture(scope="function")
def kernel_image2(kernel_image_client_super_admin: KernelImageClient):
    kernel_image = kernel_image_client_super_admin.create_kernel_image(
        parent=GLOBAL_WORKSPACE,
        kernel_image=KernelImage(
            kernel_image_type=KernelImageType.TYPE_PYTHON,
            image="something else",
        ),
        kernel_image_id="img2",
    )

    yield kernel_image
    kernel_image_client_super_admin.delete_kernel_image(name=kernel_image.name)


@pytest.fixture(scope="function")
def kernel_template(kernel_template_client_user: KernelTemplateClient):
    kt = kernel_template_client_user.create_kernel_template(
        parent=DEFAULT_WORKSPACE,
        kernel_template=KernelTemplate(
            milli_cpu_limit=200,
            gpu=1,
            memory_bytes_limit="1000",
            storage_bytes="1Gi",
            max_idle_duration="600s",
        ),
        kernel_template_id="kt1",
    )
    yield kt
    kernel_template_client_user.delete_kernel_template(name=kt.name)


@pytest.fixture(scope="function")
def kernel_template2(kernel_template_client_user: KernelTemplateClient):
    kt = kernel_template_client_user.create_kernel_template(
        parent=DEFAULT_WORKSPACE,
        kernel_template=KernelTemplate(
            milli_cpu_limit=400,
            gpu=1,
            memory_bytes_limit="1000",
            storage_bytes="1Gi",
            max_idle_duration="300s",
        ),
        kernel_template_id="kt2",
    )
    yield kt
    kernel_template_client_user.delete_kernel_template(name=kt.name)


@pytest.fixture(scope="function")
def notebook_kernel_spec(
    notebook_kernel_spec_client_super_admin: NotebookKernelSpecClient,
    kernel_image,
    kernel_template,
):
    return notebook_kernel_spec_client_super_admin.create_notebook_kernel_spec(
        parent=GLOBAL_WORKSPACE,
        notebook_kernel_spec=NotebookKernelSpec(
            kernel_image=kernel_image.name,
            kernel_template=kernel_template.name,
        ),
        notebook_kernel_spec_id="nks1",
    )


@pytest.fixture(scope="function")
def delete_all_notebook_kernel_specs_after(notebook_kernel_spec_client_super_admin: NotebookKernelSpecClient):
    yield
    notebook_kernel_spec_client_super_admin.delete_all_notebook_kernel_specs(parent=GLOBAL_WORKSPACE)
