import requests
from typing import Optional
from logging import getLogger
from datetime import datetime, timedelta

LOG = getLogger(__name__)


class ClientCredentialsConfigurationMixin:
    """
    Mixin to support client_credentials authentication flow.

    """

    def __init__(self, client_key, client_secret, access_token_url=None):
        self.client_key = client_key
        self.client_secret = client_secret
        self.access_token_url = access_token_url

        # a holder for our cached access token
        self._access_token: Optional[str] = None
        # a holder for the timestamp at which our access token expires
        self._access_token_expires_at: Optional[datetime] = None

    def auth_settings(self):
        """
        Overide the auth settings method to ensure that the access token is updated
        before being used in an API request.


        """
        self.access_token = self._get_api_gateway_access_token()
        return super().auth_settings()

    def _get_api_gateway_access_token(self):
        """
        Returns either a recently refreshed access token or the cached access token
        if still valid.

        """
        now = datetime.now()
        if (
            self._access_token is not None
            and self._access_token_expires_at is not None
            and
            # ensure that our access token is still valid - with a leeway of 20 seconds
            now < (self._access_token_expires_at - timedelta(seconds=20))
        ):
            return self._access_token

        LOG.debug("Refreshing API Gateway access token")

        auth = requests.auth.HTTPBasicAuth(self.client_key, self.client_secret)
        data = {"grant_type": "client_credentials"}

        response = requests.post(self.access_token_url, data=data, auth=auth)
        if (
            response.status_code >= 300
            or response.status_code < 200
            or not response.json().get("access_token")
        ):
            raise RuntimeError(
                f"Access token request failed: {response.status_code}, {response.text}"
            )

        response_data = response.json()
        self._access_token = response_data["access_token"]
        # the `expires_in` value is in seconds rather than milliseconds, if we don't have
        # an `expires_in` use 1 minute as a reasonable default.
        self._access_token_expires_at = now + timedelta(
            seconds=response_data.get("expires_in", 60)
        )

        return self._access_token
