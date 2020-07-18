from django.http import JsonResponse
from django.shortcuts import render
from web.utils import *
import logging
from django.conf import settings
import json
from pyecharts import options
from pyecharts.charts import Line, Pie

logger = logging.getLogger(__name__)


def api_profile_line_chart() -> Line:
    """
    接口平均耗时
    :return:
    """
    xaxis = get_xaxis_days(days=10)

    apis = list(filter(lambda x: x, R.smembers(settings.REDIS_API_KEY)))

    line = (
        Line()
        .add_xaxis(xaxis)
        .set_global_opts(title_opts=options.TitleOpts(title="API 耗时走势"),
                         yaxis_opts=options.AxisOpts(
                             is_scale=True,
                             splitline_opts=options.SplitLineOpts(is_show=True)
                         ),
                         tooltip_opts=options.TooltipOpts(trigger='axis'),
                         )
    )
    for api in apis:
        if api in get_profile_apis():
            api_redis_keys = [settings.REDIS_API_AVG_KEY % (api, day) for day in xaxis]
            api_profile = R.mget(*api_redis_keys)
            line.add_yaxis(api, api_profile, is_connect_nones=True, is_smooth=True,
                           label_opts=options.LabelOpts(is_show=False))

    return line.dump_options()


def uv_line_chart() -> Line:
    """
    UV折线图，包括总 UV、新用户 UV、注册 UV
    """
    xaxis = get_xaxis_days()

    uv_all_redis_keys = [settings.REDIS_UV_ALL_KEY % day for day in xaxis]
    uv_new_redis_keys = [settings.REDIS_UV_NEW_KEY % day for day in xaxis]
    uv_reg_redis_keys = [settings.REDIS_REG_KEY % day for day in xaxis]

    uv_all = R.mget(*uv_all_redis_keys)
    uv_new = R.mget(*uv_new_redis_keys)
    uv_reg = R.mget(*uv_reg_redis_keys)

    line = (
        Line()
        .add_xaxis(xaxis)
        .add_yaxis("总用户数（访问设备）", uv_all, is_connect_nones=True, is_smooth=True)
        .add_yaxis("新用户数（一周未访问）", uv_new, is_connect_nones=True, is_smooth=True)
        .add_yaxis("注册用户数", uv_reg, is_connect_nones=True, is_smooth=True)
        .set_global_opts(title_opts=options.TitleOpts(title="用户数走势"),
                         yaxis_opts=options.AxisOpts(
                             is_scale=True,
                             splitline_opts=options.SplitLineOpts(is_show=True)
                         ),
                         tooltip_opts=options.TooltipOpts(trigger='axis'),
                         )
        .dump_options()
    )
    return line


def refer_pv_line_chart() -> Line:
    """
    UV折线图，外域的每天流量趋势
    """
    xaxis = get_xaxis_days()

    uv_zhihu_redis_keys = [settings.REDIS_REFER_PV_DAY_KEY % ('link.zhihu.com', day) for day in xaxis]
    uv_ryf_redis_keys = [settings.REDIS_REFER_PV_DAY_KEY % ('www.ruanyifeng.com', day) for day in xaxis]
    uv_github_redis_keys = [settings.REDIS_REFER_PV_DAY_KEY % ('github.com', day) for day in xaxis]
    uv_baidu_redis_keys = [settings.REDIS_REFER_PV_DAY_KEY % ('www.baidu.com', day) for day in xaxis]
    uv_google_redis_keys = [settings.REDIS_REFER_PV_DAY_KEY % ('www.google.com', day) for day in xaxis]
    uv_wanqu_redis_keys = [settings.REDIS_REFER_PV_DAY_KEY % ('wanqu.co', day) for day in xaxis]

    uv_zhihu = R.mget(*uv_zhihu_redis_keys)
    uv_ryf = R.mget(*uv_ryf_redis_keys)
    uv_github = R.mget(*uv_github_redis_keys)
    uv_baidu = R.mget(*uv_baidu_redis_keys)
    uv_google = R.mget(*uv_google_redis_keys)
    uv_wanqu = R.mget(*uv_wanqu_redis_keys)

    line = (
        Line()
        .add_xaxis(xaxis)
        .add_yaxis("zhihu", uv_zhihu, is_connect_nones=True, is_smooth=True)
        .add_yaxis("ruanyifeng", uv_ryf, is_connect_nones=True, is_smooth=True)
        .add_yaxis("github", uv_github, is_connect_nones=True, is_smooth=True)
        .add_yaxis("baidu", uv_baidu, is_connect_nones=True, is_smooth=True)
        .add_yaxis("google", uv_google, is_connect_nones=True, is_smooth=True)
        .add_yaxis("wanqu", uv_wanqu, is_connect_nones=True, is_smooth=True)
        .set_global_opts(title_opts=options.TitleOpts(title="Referer 各域名PV走势"),
                         yaxis_opts=options.AxisOpts(
                             is_scale=True,
                             splitline_opts=options.SplitLineOpts(is_show=True)
                         ),
                         tooltip_opts=options.TooltipOpts(trigger='axis'),
                         )
        .dump_options()
    )
    return line


def refer_pie_chart() -> Pie:
    refer_hosts = list(filter(lambda x: x, R.smembers(settings.REDIS_REFER_DAY_KEY % current_day())))
    refer_host_pv_keys = [settings.REDIS_REFER_PV_DAY_KEY % (host, current_day()) for host in refer_hosts]

    c = (
        Pie()
        .add(
            "",
            [list(z) for z in zip(refer_hosts, R.mget(*refer_host_pv_keys)) if int(z[1]) > 1],
            # radius=["30%", "75%"],
            # rosetype="radius",
        )
        .set_global_opts(
            title_opts=options.TitleOpts(title="Referer 来源占比"),
            legend_opts=options.LegendOpts(
                type_="scroll", pos_left="80%", orient="vertical"
            ),
        )
        .set_series_opts(label_opts=options.LabelOpts(formatter="{b}: {c}"))
        .dump_options()
    )
    return c


def get_uv_chart_data(request):
    return JsonResponse(json.loads(uv_line_chart()))


def get_refer_pie_data(request):
    return JsonResponse(json.loads(refer_pie_chart()))


def get_refer_pv_chart_data(request):
    return JsonResponse(json.loads(refer_pv_line_chart()))


def get_api_profile_chart_data(request):
    return JsonResponse(json.loads(api_profile_line_chart()))


def dashboard(request):
    return render(request, 'dashboard/index.html')


def get_warn_log(request):
    warn_log_file = settings.LOGGING['handlers']['my_warn']['filename']
    logs = list(reversed(open(warn_log_file).read().split('\n')))[:200]

    logs = [l for l in logs if l]

    context = dict()
    context['logs'] = logs

    return render(request, 'dashboard/logs.html', context=context)

