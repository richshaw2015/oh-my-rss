
from django.http import JsonResponse
from .models import User
from django.shortcuts import redirect
import requests
from requests import ReadTimeout, ConnectTimeout, HTTPError, Timeout, ConnectionError
import logging
from django.conf import settings
import json
from PIL import Image
from io import BytesIO
import os
from .utils import add_user_sub_feeds, get_subscribe_sites, add_register_count, get_hash_name

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
                                logger.info(f"新用户登录：`{user.oauth_name}")
                                add_user_sub_feeds(oauth_id, get_subscribe_sites('', ''))
                                add_register_count()

                                # 用户头像存储到本地一份，国内网络会丢图
                                try:
                                    rsp = requests.get(oauth_avatar, timeout=10)
                                    if rsp.ok:
                                        img_obj = Image.open(BytesIO(rsp.content))
                                        img_obj.thumbnail((100, 100))
                                        jpg = get_hash_name(oauth_id) + '.jpg'

                                        if img_obj.mode != 'RGB':
                                            img_obj = img_obj.convert('RGB')
                                        img_obj.save(os.path.join(settings.AVATAR_DIR, jpg))

                                        user.avatar = f'/assets/avatar/{jpg}'
                                        user.save()
                                    else:
                                        logger.error(f"同步用户头像出现网络异常！`{oauth_id}`{oauth_avatar}")
                                except (ConnectTimeout, HTTPError, ReadTimeout, Timeout, ConnectionError):
                                    logger.error(f"同步用户头像网络异常！`{oauth_id}`{oauth_avatar}")
                                except:
                                    logger.error(f"同步用户头像未知异常！`{oauth_id}`{oauth_avatar}")

                            response = redirect('index')
                            response.set_signed_cookie('oauth_id', oauth_id, max_age=10 * 365 * 86400)
                            response.set_signed_cookie('toast', 'LOGIN_SUCC_MSG', max_age=20)
                            return response
    except (ConnectTimeout, HTTPError, ReadTimeout, Timeout, ConnectionError):
        logger.warning("OAuth 认证网络出现异常！")
    except:
        logger.warning("OAuth 认证出现未知异常！")

    response = redirect('index')
    response.set_signed_cookie('toast', 'LOGIN_ERROR_MSG', max_age=20)
    return response
