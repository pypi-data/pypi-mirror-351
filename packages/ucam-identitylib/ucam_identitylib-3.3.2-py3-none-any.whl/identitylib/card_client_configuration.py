from identitylib.card_client.configuration import Configuration
from identitylib.api_client_mixin import ClientCredentialsConfigurationMixin


class CardClientConfiguration(ClientCredentialsConfigurationMixin, Configuration):
    def __init__(
        self,
        client_key,
        client_secret,
        access_token_url="https://api.apps.cam.ac.uk/oauth2/v1/token",
        base_url="https://api.apps.cam.ac.uk/card",
    ):
        Configuration.__init__(self, host=base_url)
        ClientCredentialsConfigurationMixin.__init__(
            self, client_key, client_secret, access_token_url
        )
