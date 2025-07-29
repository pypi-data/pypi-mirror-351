# !/usr/bin/env Python3
# -*- coding: utf-8 -*-
# @Author   : zhangzhanqi
# @FILE     : casdoor.py
# @Time     : 2023/11/29 14:17
from typing import Tuple, Optional

from casdoor import CasdoorSDK
from starlette.requests import Request

from fastapix.sso._client import Client


class Casdoor(Client):

    def __init__(
            self,
            endpoint: str,
            *,
            client_id: str,
            client_secret: str,
            certificate: str,

            org_name: str,
            application_name: str,
            **kwargs
    ):
        if endpoint.endswith('/'):
            endpoint = endpoint[:-1]
        super().__init__(
            endpoint,
            **kwargs
        )
        self.sdk = CasdoorSDK(
            endpoint=endpoint,
            client_id=client_id,
            client_secret=client_secret,
            certificate=certificate,
            org_name=org_name,
            application_name=application_name,
            front_endpoint=endpoint
        )

    async def sso_login_url(self, signin_url: str) -> str:
        return self.sdk.get_auth_link(redirect_uri=signin_url)

    async def sso_logout_url(self, signout_url: str) -> str:
        return signout_url

    async def verify_user(
            self, request: Request, token=None, service_url=None
    ) -> Tuple[Optional[dict], Optional[str]]:
        if token is None:
            code = request.query_params.get("code")
            token = self.sdk.get_oauth_token(code).get("access_token")
        user = self.sdk.parse_jwt_token(token)
        return user, token
