import hashlib

import grpc
import pytest
from ai.h2o.notebook.v1.kernel_service_pb2 import ListKernelsRequest
from kubernetes import client

from h2o_notebook.clients.base.workspace import DEFAULT_WORKSPACE


def test_on_behalf_internal_service(kernel_grpc_client, workloads_namespace):
    token = create_service_account_token(namespace=workloads_namespace, service_account_name="default")
    assert token is not None

    hashed_token = hashlib.sha256(token.encode("utf-8")).hexdigest()
    request_metadata = [
        ("x-h2o-service-authorization", token),
        ("x-h2o-on-behalf-of-service", hashed_token),
        ("x-h2o-is-internal-service", "true"),
    ]

    # Testing that no error was received from server.
    kernel_grpc_client.ListKernels(
        request=ListKernelsRequest(
            parent=DEFAULT_WORKSPACE,
        ),
        metadata=request_metadata,
    )


def test_on_behalf_service(kernel_grpc_client, workloads_namespace):
    token = create_service_account_token(workloads_namespace, service_account_name="default")
    assert token is not None

    hashed_token = hashlib.sha256(token.encode("utf-8")).hexdigest()
    request_metadata = [
        ("x-h2o-service-authorization", token),
        ("x-h2o-on-behalf-of-service", hashed_token),
    ]

    # Testing that no error was received from server.
    kernel_grpc_client.ListKernels(
        request=ListKernelsRequest(
            parent=DEFAULT_WORKSPACE,
        ),
        metadata=request_metadata,
    )


def test_on_behalf_user(kernel_grpc_client, super_admin_token_provider, workloads_namespace):
    token = create_service_account_token(namespace=workloads_namespace, service_account_name="default")
    assert token is not None
    user_token = super_admin_token_provider.token()

    request_metadata = [
        ("x-h2o-service-authorization", token),
        ("authorization", f"Bearer {user_token}"),
    ]

    # Testing that no error was received from server.
    kernel_grpc_client.ListKernels(
        request=ListKernelsRequest(
            parent=DEFAULT_WORKSPACE,
        ),
        metadata=request_metadata,
    )


def test_missing_service_authorization(kernel_grpc_client, super_admin_token_provider):
    user_token = super_admin_token_provider.token()
    request_metadata = [
        ("authorization", f"Bearer {user_token}"),
    ]

    with pytest.raises(grpc.RpcError) as exc:
        kernel_grpc_client.ListKernels(
            request=ListKernelsRequest(
                parent=DEFAULT_WORKSPACE,
            ),
            metadata=request_metadata,
        )
    assert exc.value.code() == grpc.StatusCode.UNAUTHENTICATED
    assert "authentication failed: request unauthenticated" in exc.value.details()


def test_mismatched_token_hash(kernel_grpc_client, super_admin_token_provider):
    token = create_service_account_token(namespace="notebook-dev", service_account_name="default")
    assert token is not None

    request_metadata = [
        ("x-h2o-service-authorization", token),
        ("x-h2o-on-behalf-of-service", "wrong hash"),
    ]

    with pytest.raises(grpc.RpcError) as exc:
        kernel_grpc_client.ListKernels(
            request=ListKernelsRequest(
                parent=DEFAULT_WORKSPACE,
            ),
            metadata=request_metadata,
        )
    assert exc.value.code() == grpc.StatusCode.UNAUTHENTICATED
    assert "invalid x-h2o-on-behalf-of-service metadata" in exc.value.details()


def test_invalid_service_token(kernel_grpc_client, super_admin_token_provider):
    request_metadata = [
        ("x-h2o-service-authorization", "definitely not service account token"),
    ]

    with pytest.raises(grpc.RpcError) as exc:
        kernel_grpc_client.ListKernels(
            request=ListKernelsRequest(
                parent=DEFAULT_WORKSPACE,
            ),
            metadata=request_metadata,
        )
    assert exc.value.code() == grpc.StatusCode.UNAUTHENTICATED
    assert "authentication failed: invalid JWT" in exc.value.details()


def test_invalid_user_token(kernel_grpc_client, workloads_namespace):
    token = create_service_account_token(namespace=workloads_namespace, service_account_name="default")
    assert token is not None

    request_metadata = [
        ("x-h2o-service-authorization", token),
        ("authorization", f"Bearer invalid user token"),
    ]

    with pytest.raises(grpc.RpcError) as exc:
        kernel_grpc_client.ListKernels(
            request=ListKernelsRequest(
                parent=DEFAULT_WORKSPACE,
            ),
            metadata=request_metadata,
        )
    assert exc.value.code() == grpc.StatusCode.UNAUTHENTICATED
    assert "platform token authentication: parsing token: invalid compact serialization format: invalid number of segments" in exc.value.details()


def test_not_allowed_service_account(kernel_grpc_client, not_allowed_service_account):
    token = create_service_account_token(
        namespace=not_allowed_service_account.metadata.namespace,
        service_account_name=not_allowed_service_account.metadata.name,
    )
    assert token is not None

    hashed_token = hashlib.sha256(token.encode("utf-8")).hexdigest()
    request_metadata = [
        ("x-h2o-service-authorization", token),
        ("x-h2o-on-behalf-of-service", hashed_token),
    ]

    with pytest.raises(grpc.RpcError) as exc:
        kernel_grpc_client.ListKernels(
            request=ListKernelsRequest(
                parent=DEFAULT_WORKSPACE,
            ),
            metadata=request_metadata,
        )
    assert exc.value.code() == grpc.StatusCode.PERMISSION_DENIED
    assert "service account system:serviceaccount:notebook-dev:not-allowed-service-account is unauthorized" in exc.value.details()


def create_service_account_token(namespace: str, service_account_name: str) -> str:
    v1 = client.CoreV1Api()
    response = v1.create_namespaced_service_account_token(
        name=service_account_name,
        namespace=namespace,
        body=(client.V1TokenRequestSpec(audiences=['kubernetes.default.svc']))
    )

    print(f"response: {response}")

    return response.status.token
