import os

import h2o_authn
import pytest as pytest
from h2o_authn import TokenProvider

import h2o_notebook


@pytest.fixture(scope="session")
def user_clients():
    return h2o_notebook.login_custom(
        endpoint=os.getenv("NOTEBOOK_SERVER_URL"),
        refresh_token=os.getenv("PLATFORM_TOKEN_USER"),
        issuer_url=os.getenv("PLATFORM_OIDC_URL"),
        client_id=os.getenv("PLATFORM_OIDC_CLIENT_ID"),
    )


@pytest.fixture(scope="session")
def super_admin_clients():
    return h2o_notebook.login_custom(
        endpoint=os.getenv("NOTEBOOK_SERVER_URL"),
        refresh_token=os.getenv("PLATFORM_TOKEN_SUPER_ADMIN"),
        issuer_url=os.getenv("PLATFORM_OIDC_URL"),
        client_id=os.getenv("PLATFORM_OIDC_CLIENT_ID"),
    )


@pytest.fixture(scope="session")
def token_provider_user() -> TokenProvider:
    return h2o_authn.TokenProvider(
        refresh_token=os.getenv("PLATFORM_TOKEN_USER"),
        issuer_url=os.getenv("PLATFORM_OIDC_URL"),
        client_id=os.getenv("PLATFORM_OIDC_CLIENT_ID"),
    )


@pytest.fixture(scope="session")
def token_provider_super_admin() -> TokenProvider:
    return h2o_authn.TokenProvider(
        refresh_token=os.getenv("PLATFORM_TOKEN_SUPER_ADMIN"),
        issuer_url=os.getenv("PLATFORM_OIDC_URL"),
        client_id=os.getenv("PLATFORM_OIDC_CLIENT_ID"),
    )


@pytest.fixture(scope="session")
def kernel_image_client_user(user_clients):
    return user_clients.kernel_image_client


@pytest.fixture(scope="session")
def kernel_image_client_super_admin(super_admin_clients):
    return super_admin_clients.kernel_image_client


@pytest.fixture(scope="session")
def kernel_template_client_user(user_clients):
    return user_clients.kernel_template_client


@pytest.fixture(scope="session")
def kernel_template_client_super_admin(super_admin_clients):
    return super_admin_clients.kernel_template_client


@pytest.fixture(scope="session")
def notebook_kernel_spec_client_user(user_clients):
    return user_clients.notebook_kernel_spec_client


@pytest.fixture(scope="session")
def notebook_kernel_spec_client_super_admin(super_admin_clients):
    return super_admin_clients.notebook_kernel_spec_client


@pytest.fixture(scope="session")
def kernel_task_client_super_admin(super_admin_clients):
    return super_admin_clients.kernel_task_client


@pytest.fixture(scope="session")
def kernel_task_client_user(user_clients):
    return user_clients.kernel_task_client


@pytest.fixture(scope="session")
def kernel_client_user(user_clients):
    return user_clients.kernel_client


@pytest.fixture(scope="session")
def kernel_client_super_admin(super_admin_clients):
    return super_admin_clients.kernel_client
