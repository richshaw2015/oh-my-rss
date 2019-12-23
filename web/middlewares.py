# -*- coding: utf-8 -*-

import logging
import time

logger = logging.getLogger(__name__)


class StatsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_t = int(time.time() * 1000)

        response = self.get_response(request)

        end_t = int(time.time() * 1000)

        duration = end_t - start_t
        logger.info(f'接口处理时间：`{request.path}`{duration} ms')

        return response
