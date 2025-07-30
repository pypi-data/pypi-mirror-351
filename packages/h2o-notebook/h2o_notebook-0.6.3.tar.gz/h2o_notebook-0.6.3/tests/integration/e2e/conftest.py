import os

import grpc
import h2o_authn
import pytest as pytest
from ai.h2o.notebook.v1 import kernel_service_pb2_grpc
from ai.h2o.notebook.v1.kernel_service_pb2_grpc import KernelServiceStub
from kubernetes import client
from kubernetes import config
from kubernetes.client import V1ServiceAccount

from h2o_notebook.clients.base.workspace import DEFAULT_WORKSPACE
from h2o_notebook.clients.base.workspace import GLOBAL_WORKSPACE
from h2o_notebook.clients.kernel.kernel import Kernel
from h2o_notebook.clients.kernel_template.kernel_template import KernelTemplate


@pytest.fixture(scope="session")
def workloads_namespace() -> str:
    return os.getenv("NOTEBOOK_WORKLOADS_NAMESPACE")


@pytest.fixture(scope="session", autouse=True)
def load_kube_config():
    config.load_kube_config()


@pytest.fixture(scope="session")
def grpc_channel():
    channel = grpc.insecure_channel(os.getenv("NOTEBOOK_GRPC_SERVER_ADDRESS"))
    yield channel
    channel.close()


@pytest.fixture(scope="session")
def kernel_grpc_client(grpc_channel) -> KernelServiceStub:
    return kernel_service_pb2_grpc.KernelServiceStub(channel=grpc_channel)


@pytest.fixture(scope="session")
def super_admin_token_provider():
    return h2o_authn.TokenProvider(
        issuer_url=os.getenv("PLATFORM_OIDC_URL"),
        client_id=os.getenv("PLATFORM_OIDC_CLIENT_ID"),
        refresh_token=os.getenv("PLATFORM_TOKEN_SUPER_ADMIN"),
    )


@pytest.fixture(scope="function")
def not_allowed_service_account(workloads_namespace) -> V1ServiceAccount:
    service_account = client.V1ServiceAccount(
        metadata=client.V1ObjectMeta(
            name="not-allowed-service-account",
        )
    )

    yield client.CoreV1Api().create_namespaced_service_account(
        namespace=workloads_namespace,
        body=service_account,
    )

    client.CoreV1Api().delete_namespaced_service_account(
        name="not-allowed-service-account",
        namespace=workloads_namespace,
    )


@pytest.fixture(scope="session")
def kernel_template_local_user(
    kernel_template_client_super_admin,
    kernel_template_client_user,
    kernel_client_super_admin,
):
    kt = kernel_template_client_user.create_kernel_template(
        parent=DEFAULT_WORKSPACE,
        kernel_template=KernelTemplate(
            milli_cpu_limit=0,
            gpu=0,
            memory_bytes_limit="1Gi",
            max_idle_duration="1h",
        ),
        kernel_template_id="kernel-template-local-user",
    )
    yield kt
    kernel_client_super_admin.wait_all_kernels_deleted(parent=DEFAULT_WORKSPACE)
    kernel_template_client_super_admin.delete_kernel_template(name=kt.name)


@pytest.fixture(scope="session")
def kernel_template_local_user_low_idle_limit(
    kernel_template_client_super_admin,
    kernel_template_client_user,
    kernel_client_super_admin,
):
    kernel_template = kernel_template_client_user.create_kernel_template(
        parent=DEFAULT_WORKSPACE,
        kernel_template=KernelTemplate(
            milli_cpu_limit=0,
            gpu=0,
            memory_bytes_limit="1Gi",
            max_idle_duration="5s",
        ),
        kernel_template_id="kernel-template-local-user-low-idle-limit",
    )
    yield kernel_template
    kernel_client_super_admin.wait_all_kernels_deleted(parent=DEFAULT_WORKSPACE)
    kernel_template_client_super_admin.delete_kernel_template(name=kernel_template.name)


@pytest.fixture(scope="session")
def kernel_template_local_user_low_memory_limit(
    kernel_template_client_super_admin,
    kernel_template_client_user,
    kernel_client_super_admin,
):
    kernel_template = kernel_template_client_user.create_kernel_template(
        parent=DEFAULT_WORKSPACE,
        kernel_template=KernelTemplate(
            milli_cpu_limit=0,
            gpu=0,
            memory_bytes_limit="100Mi",
            max_idle_duration="1h",
        ),
        kernel_template_id="kernel-template-local-user-low-memory-limit",
    )
    yield kernel_template
    kernel_client_super_admin.wait_all_kernels_deleted(parent=DEFAULT_WORKSPACE)
    kernel_template_client_super_admin.delete_kernel_template(name=kernel_template.name)


@pytest.fixture(scope="function")
def delete_all_kernels_after(kernel_client_super_admin):
    yield
    kernel_client_super_admin.delete_all_kernels(parent=DEFAULT_WORKSPACE)


@pytest.fixture(scope="module")
def kernel_python_user(kernel_client_user, kernel_template_local_user):
    k = kernel_client_user.create_kernel(
        parent=DEFAULT_WORKSPACE,
        kernel=Kernel(
            kernel_image=f"{GLOBAL_WORKSPACE}/kernelImages/python",
            kernel_template=kernel_template_local_user.name,
        ),
    )
    name = k.name
    yield k
    kernel_client_user.delete_kernel(name=name)


@pytest.fixture(scope="module")
def kernel_python_user_low_idle_limit(kernel_client_user, kernel_template_local_user_low_idle_limit):
    k = kernel_client_user.create_kernel(
        parent=DEFAULT_WORKSPACE,
        kernel=Kernel(
            kernel_image=f"{GLOBAL_WORKSPACE}/kernelImages/python",
            kernel_template=kernel_template_local_user_low_idle_limit.name,
        ),
    )
    name = k.name
    yield k
    kernel_client_user.delete_kernel(name=name)


@pytest.fixture(scope="module")
def kernel_python_user_low_idle_limit2(kernel_client_user, kernel_template_local_user_low_idle_limit):
    k = kernel_client_user.create_kernel(
        parent=DEFAULT_WORKSPACE,
        kernel=Kernel(
            kernel_image=f"{GLOBAL_WORKSPACE}/kernelImages/python",
            kernel_template=kernel_template_local_user_low_idle_limit.name,
        ),
    )
    name = k.name
    yield k
    kernel_client_user.delete_kernel(name=name)


@pytest.fixture(scope="module")
def kernel_python_user_low_memory_limit(kernel_client_user, kernel_template_local_user_low_memory_limit):
    k = kernel_client_user.create_kernel(
        parent=DEFAULT_WORKSPACE,
        kernel=Kernel(
            kernel_image=f"{GLOBAL_WORKSPACE}/kernelImages/python",
            kernel_template=kernel_template_local_user_low_memory_limit.name,
        ),
    )
    name = k.name
    yield k
    kernel_client_user.delete_kernel(name=name)
