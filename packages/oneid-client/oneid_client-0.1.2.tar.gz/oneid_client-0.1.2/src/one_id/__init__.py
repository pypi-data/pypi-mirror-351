import requests
from typing import Any, Dict

from exceptions import OneIDError
from schemas import User


class OneID:
    def __init__(self, url: str, client_id: str, client_secret: str, redirect_uri: str):
        self.url = url
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

    def get_user_info(self, code: str) -> User:
        """
        Gets user information using the authorization code.

        :param code: The authorization code received from OneID.
        :return: User object containing user details.
        """
        user_data = self._get_user_data(code)
        return User(**user_data)

    def _get_user_data(self, code: str) -> Dict[str, Any]:
        access_token = self._get_access_token(code)

        payload = {
            "grant_type": "one_access_token_identify",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "access_token": access_token,
            "scope": "my_portal"
        }

        try:
            response = requests.post(url=self.url, data=payload)
            response.raise_for_status()
        except requests.RequestException as e:
            raise OneIDError(f"Failed to fetch user data: {e}")

        return response.json()

    def _get_access_token(self, code: str) -> str:
        payload = {
            "grant_type": "one_authorization_code",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
            "code": code
        }

        try:
            response = requests.post(url=self.url, data=payload)
            response.raise_for_status()
        except requests.RequestException as e:
            raise OneIDError(f"Failed to fetch access token: {e}")

        data = response.json()
        if 'access_token' not in data:
            raise OneIDError("Access token missing in response")

        return data['access_token']