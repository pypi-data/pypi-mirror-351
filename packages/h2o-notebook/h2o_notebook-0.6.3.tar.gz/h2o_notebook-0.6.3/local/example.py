import h2o_notebook
from h2o_notebook.clients.base.workspace import GLOBAL_WORKSPACE

# Manually specifying login parameters.
client = h2o_notebook.login_custom(
    endpoint="https://notebook-api.cloud-dev.h2o.ai",
    refresh_token="<refresh token>",
    client_id="hac-platform-public",
    issuer_url="https://auth.cloud-dev.h2o.ai/auth/realms/hac-dev",
).kernel_image_client
print(client.list_all_kernel_images(parent=GLOBAL_WORKSPACE))

# Using discovery service.
client = h2o_notebook.login(environment="https://cloud-dev.h2o.ai").kernel_image_client
print(client.list_all_kernel_images(parent=GLOBAL_WORKSPACE))
