import os
import time
from typing import Callable
from typing import Optional

import h2o_authn
import h2o_discovery
import h2o_drive
import IPython

# Name of the platform client in the discovery response.
PLATFORM_CLIENT_NAME = "platform"

class Session:
    def __init__(
            self,
            environment_url: Optional[str] = None,
            config_path: str = None,
            platform_token: Optional[str] = None,
            token_provider: Callable[[], str] = None,
    ) -> None:
        """Initializes session.

        :param environment_url: Override for the URL of the environment passed to the discovery service.
        :param config_path: Override path to the h2o cli config file passed to the discovery service.
        :param platform_token: Platform token. If not provided, the token will be discovered.
        :param token_provider: Token provider. If not provided, the provider will be constructed from the discovered config.
        """
        if token_provider is not None:
            # Test token refresh
            token_provider()
            self.token_provider = token_provider
            return

        # Discover connection configuration
        d = h2o_discovery.discover(environment=environment_url, config_path=config_path)

        # Get discovery object containing public URIs
        d2 = h2o_discovery.discover(environment=d.environment.h2o_cloud_environment)

        # Discover platform_token if not provided
        if not platform_token:
            platform_token = d.credentials[PLATFORM_CLIENT_NAME].refresh_token

        # Discover client id
        client_id = d.clients.get(PLATFORM_CLIENT_NAME).oauth2_client_id
        if not client_id:
            raise ConnectionError(
                "Unable to discover platform oauth2_client_id connection value."
            )

        # Initialize token provider
        token_provider = h2o_authn.TokenProvider(
            issuer_url=d.environment.issuer_url,
            client_id=client_id,
            refresh_token=platform_token,
        )
        # Test token refresh
        token_provider()

        # Initialize async token provider
        async_token_provider = h2o_authn.AsyncTokenProvider(
            issuer_url=d.environment.issuer_url,
            client_id=client_id,
            refresh_token=platform_token,
        )

        self.token_provider = token_provider
        self.async_token_provider = async_token_provider
        self.discovery = d
        self.public_discovery = d2

    def get_token_provider(self) -> Callable[[], str]:
        """Returns token provider."""
        return self.token_provider

    def get_async_token_provider(self) -> Callable[[], str]:
        """Returns asynchronous token provider."""
        return self.async_token_provider

    async def download_file(self, path: str) -> None:
        """Download file from Kernel filesystem."""
        
        # Init H2O Drive client
        drive_client = await h2o_drive.Drive(token=self.async_token_provider, endpoint_url=self.public_discovery.services["drive"].uri)

        # Prepare new space for the file
        notebook_downloads_space = drive_client.my_bucket().with_prefix("notebook-downloads/")
        object_name = f"{time.time_ns()}/{os.path.basename(path)}"

        # Upload the file
        await notebook_downloads_space.upload_file(path, object_name)

        # Generate presigned URL for the file
        url = await notebook_downloads_space.generate_presigned_url(object_name)

        # Open the URL in a new tab of the browser which downloads the file
        IPython.display.display(IPython.display.Javascript(f'window.open("{url}");'))
