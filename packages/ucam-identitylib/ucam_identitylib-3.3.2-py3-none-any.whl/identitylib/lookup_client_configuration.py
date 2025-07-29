from identitylib.lookup_client.configuration import Configuration
from identitylib.api_client_mixin import ClientCredentialsConfigurationMixin


class LookupClientConfiguration(ClientCredentialsConfigurationMixin, Configuration):
    def __init__(
        self,
        client_key,
        client_secret,
        access_token_url="https://api.apps.cam.ac.uk/oauth2/v1/token",
        base_url="https://api.apps.cam.ac.uk/lookup/v1",
    ):
        Configuration.__init__(self, host=base_url)
        ClientCredentialsConfigurationMixin.__init__(
            self, client_key, client_secret, access_token_url
        )
