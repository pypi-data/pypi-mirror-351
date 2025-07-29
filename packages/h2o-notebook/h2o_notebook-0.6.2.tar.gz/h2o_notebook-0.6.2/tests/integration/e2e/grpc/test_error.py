import hashlib

import grpc
import pytest
from ai.h2o.notebook.v1.kernel_service_pb2 import ListKernelsRequest

from h2o_notebook.clients.base.workspace import DEFAULT_WORKSPACE
from tests.integration.e2e.grpc.test_auth import create_service_account_token


def test_bad_request(kernel_grpc_client, workloads_namespace):
    token = create_service_account_token(workloads_namespace, service_account_name="default")
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
                page_size=-1,
            ),
            metadata=request_metadata,
        )
    assert exc.value.code() == grpc.StatusCode.INVALID_ARGUMENT
    assert "validation error: page_size must be >= 0, actual value = -1" in exc.value.details()
