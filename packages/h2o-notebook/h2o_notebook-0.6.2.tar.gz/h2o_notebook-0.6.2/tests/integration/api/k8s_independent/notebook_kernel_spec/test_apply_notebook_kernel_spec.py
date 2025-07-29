from typing import List

from h2o_notebook.clients.base.workspace import GLOBAL_WORKSPACE
from h2o_notebook.clients.kernel_image.kernel_image import KernelImage
from h2o_notebook.clients.kernel_template.kernel_template import KernelTemplate
from h2o_notebook.clients.notebook_kernel_spec.client import NotebookKernelSpecClient
from h2o_notebook.clients.notebook_kernel_spec.notebook_kernel_spec import (
    NotebookKernelSpec,
)
from h2o_notebook.clients.notebook_kernel_spec.notebook_kernel_spec_config import (
    NotebookKernelSpecConfig,
)


def test_apply_notebook_kernel_specs(
    notebook_kernel_spec_client_super_admin: NotebookKernelSpecClient,
    kernel_image: KernelImage,
    kernel_template: KernelTemplate,
    delete_all_notebook_kernel_specs_after,
):
    k1 = NotebookKernelSpecConfig(
        notebook_kernel_spec_id="spec1",
        kernel_image=kernel_image.name,
        kernel_template=kernel_template.name,
        display_name="spec 1",
        disabled=False,
    )
    k2 = NotebookKernelSpecConfig(
        notebook_kernel_spec_id="spec2",
        kernel_image=kernel_image.name,
        kernel_template=kernel_template.name,
        display_name="spec 2",
        disabled=True,
    )
    k3 = NotebookKernelSpecConfig(
        notebook_kernel_spec_id="spec3",
        kernel_image=kernel_image.name,
        kernel_template=kernel_template.name,
        display_name="spec 3",
        disabled=False,
    )

    configs = [k1, k2, k3]

    notebook_kernel_specs = notebook_kernel_spec_client_super_admin.apply_notebook_kernel_specs(configs)

    want = [
        NotebookKernelSpec(
            name=f"{GLOBAL_WORKSPACE}/notebookKernelSpecs/spec3",
            kernel_image=kernel_image.name,
            kernel_template=kernel_template.name,
            display_name="spec 3",
            disabled=False,
        ),
        NotebookKernelSpec(
            name=f"{GLOBAL_WORKSPACE}/notebookKernelSpecs/spec2",
            kernel_image=kernel_image.name,
            kernel_template=kernel_template.name,
            display_name="spec 2",
            disabled=True,
        ),
        NotebookKernelSpec(
            name=f"{GLOBAL_WORKSPACE}/notebookKernelSpecs/spec1",
            kernel_image=kernel_image.name,
            kernel_template=kernel_template.name,
            display_name="spec 1",
            disabled=False,
        ),
    ]

    assert_notebook_kernel_specs_equal(want, notebook_kernel_specs)

    notebook_kernel_specs = notebook_kernel_spec_client_super_admin.list_all_notebook_kernel_specs(
        parent=GLOBAL_WORKSPACE,
    )
    assert_notebook_kernel_specs_equal(want, notebook_kernel_specs)


def assert_notebook_kernel_specs_equal(want: List[NotebookKernelSpec], images: List[NotebookKernelSpec]):
    assert len(want) == len(images)

    for i in range(len(want)):
        assert want[i].name == images[i].name
        assert want[i].display_name == images[i].display_name
        assert want[i].kernel_image == images[i].kernel_image
        assert want[i].kernel_template == images[i].kernel_template
        assert want[i].disabled == images[i].disabled
