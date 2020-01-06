
from django.http import JsonResponse
from .models import User
from django.shortcuts import redirect
import requests
from requests import ReadTimeout, ConnectTimeout, HTTPError, Timeout, ConnectionError
import logging
from django.conf import settings
import json
from .utils import add_user_sub_feeds, get_subscribe_sites

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
                        if rsp.json().get('id'):
                            oauth_id = f'github/{rsp.json()["id"]}'
                            oauth_name = rsp.json().get('name') or rsp.json().get('login')
                            oauth_avatar = rsp.json().get('avatar_url')
                            oauth_email = rsp.json().get('email')
                            oauth_blog = rsp.json().get('blog') or rsp.json().get('url')
                            oauth_ext = json.dumps(rsp.json())

                            # 用户信息入库 TODO 用户头像存储到本地一份，国内网络会丢图
                            user, created = User.objects.update_or_create(
                                oauth_id=oauth_id, 
                                defaults={
                                    "oauth_name": oauth_name,
                                    "oauth_avatar": oauth_avatar,
                                    "oauth_email": oauth_email,
                                    "oauth_blog": oauth_blog,
                                    "oauth_ext": oauth_ext,
                            })
                            if created:
                                logger.info(f"新用户登录：`{user.oauth_name}")
                                # 给新用户默认推荐列表 TODO 消息通知
                                add_user_sub_feeds(oauth_id, get_subscribe_sites('', ''))

                            response = redirect('index')
                            response.set_signed_cookie('oauth_id', oauth_id, max_age=10 * 365 * 86400)
                            return response
    except (ConnectTimeout, HTTPError, ReadTimeout, Timeout, ConnectionError):
        logger.warning("OAuth 认证网络出现异常！")
    except:
        logger.warning("OAuth 认证出现未知异常！")
    # TODO 返回错误提示信息
    return redirect('index')
