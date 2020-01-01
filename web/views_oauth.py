
from django.http import JsonResponse
from .models import *
from django.shortcuts import redirect
import requests
from requests import ReadTimeout, ConnectTimeout, HTTPError, Timeout, ConnectionError
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


def github_callback(request):
    """
    接收 github 的登录回调
    """
    try:
        code = request.GET.get('code')

        if code:
            rsp = requests.post('https://github.com/login/oauth/access_token', data={
                "client_id": settings.GITHUB_OAUTH_KEY,
                "client_secret": settings.GITHUB_OAUTH_SECRET,
                "code": code,
            }, headers={"Accept": "application/json"}, timeout=8)

            if rsp.ok:
                access_token = rsp.json().get('access_token')

                if access_token:
                    rsp = requests.get('https://api.github.com/user', headers={
                        "Accept": "application/json",
                        "Authorization": f"token {access_token}",
                    }, timeout=8)

                    if rsp.ok:
                        logger.info(rsp.json())
                        # TODO 入库处理
                        login_id = f'github/{rsp.json()["id"]}'

                        response = redirect('index')
                        response.set_signed_cookie('login_id', login_id, max_age=10 * 365 * 86400)
                        return response
    except (ConnectTimeout, HTTPError, ReadTimeout, Timeout, ConnectionError):
        logger.warning("OAuth 认证异常！")
    # TODO 返回错误提示信息
    return redirect('index')
