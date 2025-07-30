import os
from typing import Optional, Any

import requests


token_endpoint = "https://auth.tesla.com/oauth2/v3/token"
base_url = "https://fleet-api.prd.na.vn.cloud.tesla.com/api/1/"  # Todo: localize


class TeslaService:
    """Provides functionality for calling endpoints while automatically fetching/handling tokens.

    To instantiate a new TeslaService, your client ID is required so that fresh tokens can be retrieved.
    A refresh token is also required (as an argument or stored in tesla.tkn) to avoid an access token going stale.

    If this is all new to you, you can walk through the steps provided by https://www.myteslamate.com/
    """
    def __init__(self, client_id: str, refresh_token: str = None):
        self.client_id = client_id
        if refresh_token:
            self.refresh_token = refresh_token
        elif not os.path.exists("tesla.tkn"):
            raise Exception("No refresh token found")

    @property
    def refresh_token(self) -> str:
        """Reads the currently stored refresh token

        :return: The latest refresh token
        """
        with open("tesla.tkn", "r") as f:
            return f.read()

    @refresh_token.setter
    def refresh_token(self, token: str) -> None:
        with open("tesla.tkn", "w") as f:
            # TODO: token is currently stored in plaintext and thus readable byo anyone who may have access to machine
            f.write(token)

    @property
    def _form_data(self) -> dict[str, str]:
        """Returns the form data used for requesting a new token"""
        return {
            "grant_type": "refresh_token",
            "client_id": self.client_id,
            "refresh_token": self.refresh_token
        }

    @property
    def access_token(self) -> str:
        """Retrieves a new access token to use for other API calls.

        A new refresh token is also retrieved and stored as the old one is used in this process.

        :return: A new access token
        """
        # TODO: reuse access token more than once
        response = requests.post(token_endpoint, data=self._form_data).json()
        self.refresh_token = response["refresh_token"]
        return response["access_token"]

    @property
    def headers(self) -> dict[str, str]:
        """Builds the HTTP headers needed to make a request.

        The headers include authorization which is required in most cases.

        :return: A dict containing authorization details
        """
        return {"Authorization": f"Bearer {self.access_token}"}

    def get(self, endpoint: str, resource_id: Optional[str] = None, path: Optional[str] = None, **params) -> Any:
        """Conducts a GET Request against the Tesla API.

        :param endpoint: endpoint to call
        :param resource_id: ID of the resource if applicable
        :param path: path indicating the action to take upon the resource
        :param params: any additional parameters to pass to the endpoint
        :return: The response data which may be of any primitive type but is often a dict
        """
        if resource_id:
            endpoint = f"{endpoint}/{resource_id}"
        if path:
            endpoint = f"{endpoint}/{path}"
        response = requests.get(endpoint, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()["response"]

    def post(self,
            endpoint: str,
            resource_id: Optional[str] = None,
            path: Optional[str] = None,
            data: Optional[dict] = None, **params):
        """Conducts a POST request against the Tesla API.

        :param endpoint: endpoint to call
        :param resource_id: ID of the resource on which to act
        :param path: path indicating the action to take upon the resource
        :param data: request body to include with the call
        :return: The response data which may be of any primitive type but is often a dict
        """
        if resource_id:
            endpoint = f"{endpoint}/{resource_id}"
        if path:
            endpoint = f"{endpoint}/{path}"
        response = requests.post(endpoint, data=data, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()["response"]

    def delete(self, endpoint: str, resource_id: str, path: Optional[str] = None) -> Any:
        """Conducts a DELETE request against the Tesla API.

        :param endpoint: endpoint to call
        :param resource_id: ID of the resource on which to act
        :param path: specific data on the resource, if any, to delete
        :return: The response data, if any, indicating the resulting change
        """
        endpoint = f"{endpoint}/{resource_id}"
        if path:
            endpoint = f"{endpoint}/{path}"
        response = requests.delete(endpoint, headers=self.headers)
        response.raise_for_status()
        return response.json()["response"]
