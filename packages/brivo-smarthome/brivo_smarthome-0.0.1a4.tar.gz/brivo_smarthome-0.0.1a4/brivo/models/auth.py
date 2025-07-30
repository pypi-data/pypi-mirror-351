import typing
from datetime import datetime

import httpx


class BrivoAuth(httpx.Auth):
    HEADERS = {'accept': 'application/json'}

    def __init__(self, base_url: str, username: str, password: str):
        self.username: str = username
        self.password: str = password
        self.base_url: str = base_url
        self._access_token: str | None = None
        self._refresh_token: str | None = None
        self._token_expires_at: datetime = datetime.now()

    @property
    def authenticated(self) -> bool:
        return self._access_token is not None

    def build_authentication_request(self) -> httpx.Request:
        url = self.base_url + '/v1/login'
        payload = {
            'username': self.username,
            'password': self.password
        }
        return httpx.Request("POST", url, headers=self.HEADERS, json=payload)

    def build_refresh_request(self) -> httpx.Request:
        url = self.base_url + '/v1/refresh'  # Unknown endpoint
        payload = {
            'refresh_token': self._refresh_token
        }
        return httpx.Request("POST", url, headers=self.HEADERS, json=payload)

    def _update_token(self, response: httpx.Response):
        response.raise_for_status()
        body = response.json()
        self._token_expires_at = datetime.fromisoformat(body['expires_on'])
        self._access_token = body['token']
        self._refresh_token = body['refresh_token']

    def sync_auth_flow(self, request: httpx.Request) -> typing.Generator[httpx.Request, httpx.Response, None]:
        if self._token_expires_at < datetime.now(self._token_expires_at.tzinfo):  # if token is expired
            response = yield self.build_authentication_request()
            response.read()
            self._update_token(response)
        request.headers['authorization'] = f'Token {self._access_token}'
        yield request

    async def async_auth_flow(self, request: httpx.Request) -> typing.AsyncGenerator[httpx.Request, httpx.Response]:
        if self._token_expires_at < datetime.now(self._token_expires_at.tzinfo):  # if token is expired
            response = yield self.build_authentication_request()
            await response.aread()
            self._update_token(response)
        request.headers['authorization'] = f'Token {self._access_token}'
        yield request
