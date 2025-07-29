# !/usr/bin/env Python3
# -*- coding: utf-8 -*-
# @Author   : zhangzhanqi
# @FILE     : client.py
# @Time     : 2023/11/29 12:35
from typing import Optional, Literal, Tuple

from urllib import parse as urllib_parse

from fastapi import HTTPException, APIRouter, Query, Header, Depends
from fastapi.requests import Request
from fastapi.responses import RedirectResponse

from fastapix.responses import DataResponse

SESSION_KEY = 'fastapix-session'
TOKEN_KEY = 'fastapix-token'


class Client:

    def __init__(
            self,
            endpoint: str,
            proxy: str = None,
            mode: Literal['session', 'token'] = 'session',
            **kwargs
    ):
        """

        :param endpoint: SSO 认证服务
        :param proxy: 代理地址 e: http://lcoalhost:80/api/fastapix
        :param client_id:
        :param client_secret:
        :param certificate:
        :param org_name:
        :param application_name:
        :param session_secret_type:
        :param session_secret_key:
        """
        self.endpoint = endpoint
        self.proxy = proxy
        self.mode = mode

    def authenticate_user_for_session(self, request: Request):
        try:
            user = request.session.get(SESSION_KEY, None)
            if user:
                return user
            else:
                raise HTTPException(status_code=401, detail='Unauthorized')
        except BaseException as _:
            raise HTTPException(status_code=401, detail='Unauthorized')

    def authenticate_user_for_token(self, request: Request, token: str = Header(..., alias=TOKEN_KEY)):
        try:
            user = self.verify_user(request=request, token=token)
            if user:
                return user
            else:
                raise HTTPException(status_code=401, detail='Unauthorized')
        except BaseException as _:
            raise HTTPException(status_code=401, detail='Unauthorized')

    @property
    def authenticate_user(self):
        if self.mode == 'session':
            return self.authenticate_user_for_session
        elif self.mode == 'token':
            return self.authenticate_user_for_token

    def router(
            self,
            prefix='/sso',
            tags=None
    ) -> APIRouter:
        if tags is None:
            tags = ['SSO']
        router = APIRouter(prefix=prefix, tags=tags)

        signin_path: str = '/signin'
        signout_path: str = '/signout'

        @router.get(signin_path, include_in_schema=False)
        @router.post(signin_path, include_in_schema=False)
        async def signin(request: Request, redirect: str = Query(...)):
            query = urllib_parse.urlencode({'redirect': redirect})
            signin_url = str(request.url.replace(query=query))
            if self.proxy:
                signin_url = urllib_parse.urljoin(self.proxy, signin_url.split("/", 3)[3])
            user, token = await self.verify_user(request=request, service_url=signin_url)
            if self.mode == 'session':
                request.session[SESSION_KEY] = user
                return RedirectResponse(redirect)
            elif self.mode == 'token':
                headers = {TOKEN_KEY: token}
                return RedirectResponse(redirect, headers=headers)

        @router.get(signout_path, include_in_schema=False)
        @router.post(signout_path, include_in_schema=False)
        async def signout(request: Request, redirect: str = Query(...)):
            if SESSION_KEY in request.session:
                request.session.pop(SESSION_KEY)
            return RedirectResponse(redirect)

        @router.get('/toLogin', description=f'[重定向到此地址以完成登录](#/{prefix}/toLogin)')
        async def to_login(request: Request, redirect: Optional[str] = Query(None)):
            redirect = redirect or self.proxy or '/docs'

            parent_url = str(request.url).split('/toLogin')[0]
            if self.proxy:
                parent_url = urllib_parse.urljoin(self.proxy, parent_url.split("/", 3)[3])
            query = urllib_parse.urlencode({'redirect': redirect})
            signin_url = parent_url + signin_path + '?' + query
            return RedirectResponse(await self.sso_login_url(signin_url))

        @router.get('/toLogout', description=f'[重定向到此地址以完成退出](#/{prefix}/toLogout)')
        async def to_logout(request: Request, redirect: Optional[str] = Query(None)):
            redirect = redirect or self.proxy or '/docs'

            parent_url = str(request.url).split('/toLogout')[0]
            if self.proxy:
                parent_url = urllib_parse.urljoin(self.proxy, parent_url.split("/", 3)[3])
            query = urllib_parse.urlencode({'redirect': redirect})
            signout_url = parent_url + signout_path + '?' + query
            return RedirectResponse(await self.sso_logout_url(signout_url))

        @router.get("/me", tags=['SSO'])
        async def get_me(user=Depends(self.authenticate_user)):
            return DataResponse(data=user)

        return router

    async def sso_login_url(self, signin_url: str) -> str:
        raise NotImplementedError

    async def sso_logout_url(self, signout_url: str) -> str:
        raise NotImplementedError

    async def verify_user(
            self, request: Request, token=None, service_url=None
    ) -> Tuple[Optional[dict], Optional[str]]:
        raise NotImplementedError
