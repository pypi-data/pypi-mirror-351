# !/usr/bin/env Python3
# -*- coding: utf-8 -*-
# @Author   : zhangzhanqi
# @FILE     : _cas.py
# @Time     : 2023/11/29 13:24
from typing import Tuple, Optional
from urllib import parse as urllib_parse

from fastapi.requests import Request

from fastapix.sso._casx import CASClient as CASClientX
from fastapix.sso._client import Client


class CASClient(Client):

    def __init__(
            self,
            endpoint: str,
            *,
            version=3,
            **kwargs
    ):
        super().__init__(endpoint, **kwargs)

        self.cas_client = CASClientX(
            version=version,
            service_url=None,
            server_url=endpoint,
            verify_ssl_certificate=False
        )

    async def sso_login_url(self, signin_url: str) -> str:
        url = urllib_parse.urljoin(self.endpoint, 'login')
        query = urllib_parse.urlencode({'service': signin_url})
        return url + '?' + query

    async def sso_logout_url(self, signout_url: str) -> str:
        return self.cas_client.get_logout_url(signout_url)

    async def verify_user(
            self, request: Request, ticket=None, service_url=None
    ) -> Tuple[Optional[dict], Optional[str]]:
        if ticket is None:
            ticket = request.query_params.get('ticket')
        account, attributes, _ = self.cas_client.verify_ticket(ticket, service_url)
        if account is None:
            return None, ticket
        user = {"account": account, **attributes}
        return user, ticket
