# -*- coding: utf-8 -*-

import logging
import time
from .utils import add_api_profile

logger = logging.getLogger(__name__)


class StatsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_t = int(time.time() * 1000)

        response = self.get_response(request)

        end_t = int(time.time() * 1000)

        elapsed = end_t - start_t
        if elapsed > 100:
            logger.info(f'接口处理时间：`{request.path}`{elapsed} ms')
            add_api_profile(request.path, elapsed)

        return response
