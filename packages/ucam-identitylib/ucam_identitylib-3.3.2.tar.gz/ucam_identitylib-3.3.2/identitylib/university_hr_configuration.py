from identitylib.hr_client.configuration import Configuration
from identitylib.api_client_mixin import ClientCredentialsConfigurationMixin


class UniversityHRClientConfiguration(ClientCredentialsConfigurationMixin, Configuration):
    def __init__(
        self,
        client_key,
        client_secret,
        access_token_url="https://api.apps.cam.ac.uk/oauth2/v1/token",
        base_url="https://api.apps.cam.ac.uk/university-human-resources/v1alpha2",
    ):
        ClientCredentialsConfigurationMixin.__init__(
            self, client_key, client_secret, access_token_url
        )
        Configuration.__init__(self, host=base_url)
