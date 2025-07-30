# !/usr/bin/env Python3
# -*- coding: utf-8 -*-
# @Author   : zhangzhanqi
# @FILE     : __init__.py
# @Time     : 2023/11/16 16:37
__version__ = "0.10.7"


from fastapi import FastAPI

from .main import run, main


def mount(
        fastapi: FastAPI,
        *,
        enable_exception_handlers: bool = True,
        enable_offline_openapi: bool = True,
):
    if enable_exception_handlers:
        from fastapix.handlers import register_exception_handlers
        register_exception_handlers(fastapi)
    if enable_offline_openapi:
        from fastapix.offline import register_offline_openapi
        register_offline_openapi(fastapi)
