# !/usr/bin/env Python3
# -*- coding: utf-8 -*-
# @Author   : zhangzhanqi
# @FILE     : handlers.py
# @Time     : 2023/10/29 17:38
import logging
from types import FrameType

from loguru import logger


class InterceptHandler(logging.Handler):
    def __init__(self, level: int = logging.NOTSET) -> None:

        super().__init__(level)

    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame: FrameType = frame.f_back  # type: ignore
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )
