
from web.models import User
from django.shortcuts import redirect
import requests
from requests import HTTPError, Timeout, ConnectionError
import logging
from django.conf import settings
import json
from web.utils import add_user_sub_feeds, get_visitor_subscribe_feeds, add_register_count, save_avatar

logger = logging.getLogger(__name__)


def github_callback(request):
    """
    接收 github 的登录回调
    """
    logger.info(request.build_absolute_uri())

    try:
        code = request.GET.get('code')
        if code:
            rsp = requests.post('https://github.com/login/oauth/access_token', data={
                "client_id": settings.GITHUB_OAUTH_KEY,
                "client_secret": settings.GITHUB_OAUTH_SECRET,
                "code": code,
            }, headers={"Accept": "application/json"}, timeout=10)

            if rsp.ok:
                access_token = rsp.json().get('access_token')

                if access_token:
                    rsp = requests.get('https://api.github.com/user', headers={
                        "Accept": "application/json",
                        "Authorization": f"token {access_token}",
                    }, timeout=10)

                    if rsp.ok:
                        if rsp.json().get('id'):
                            oauth_id = f'github/{rsp.json()["id"]}'
                            oauth_name = rsp.json().get('name') or rsp.json().get('login')
                            oauth_avatar = rsp.json().get('avatar_url')
                            oauth_email = rsp.json().get('email')
                            oauth_blog = rsp.json().get('blog') or rsp.json().get('html_url')
                            oauth_ext = json.dumps(rsp.json())

                            # 用户信息入库
                            user, created = User.objects.update_or_create(
                                oauth_id=oauth_id, 
                                defaults={
                                    "oauth_name": oauth_name,
                                    "oauth_avatar": oauth_avatar,
                                    "oauth_email": oauth_email,
                                    "oauth_blog": oauth_blog,
                                    "oauth_ext": oauth_ext,
                                }
                            )

                            if created:
                                logger.warning(f"欢迎新用户登录：`{user.oauth_name}")
                                add_user_sub_feeds(oauth_id, get_visitor_subscribe_feeds('', '', star=28))
                                add_register_count()

                                # 用户头像存储到本地一份，国内网络会丢图
                                avatar = save_avatar(oauth_avatar, oauth_id)

                                user.avatar = avatar
                                user.save()

                            response = redirect('index')
                            response.set_signed_cookie('oauth_id', oauth_id, max_age=10 * 365 * 86400)
                            response.set_signed_cookie('toast', 'LOGIN_SUCC_MSG', max_age=20)

                            return response
    except (HTTPError, Timeout, ConnectionError):
        logger.warning("OAuth 认证网络出现异常！")
    except:
        logger.error("OAuth 认证出现未知异常")

    response = redirect('index')
    response.set_signed_cookie('toast', 'LOGIN_ERROR_MSG', max_age=20)

    return response
