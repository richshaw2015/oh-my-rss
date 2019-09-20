from django.http import HttpResponseForbidden
from web.utils import *


def verify_request(func):
    """
    verify user request
    """

    def wrapper(request):
        uid = request.POST.get('uid', '')
        if not uid:
            return HttpResponseForbidden()
        else:
            try:
                if is_visit_today(uid):
                    pass
                else:
                    # 总用户数+1
                    incr_redis_key(settings.REDIS_UV_ALL_KEY % current_day())

                    # 是否新用户
                    if not is_old_user(uid):
                        incr_redis_key(settings.REDIS_UV_NEW_KEY % current_day())

                    # 变成老用户
                    set_old_user(uid)
                    # 访问过了
                    set_visit_today(uid)
            except redis.exceptions.ConnectionError:
                logger.warning("统计UV出现异常")
        return func(request)

    return wrapper


