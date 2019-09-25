from django.http import JsonResponse
from django.shortcuts import render
from .utils import *
import logging
import json
from pyecharts import options
from pyecharts.charts import Line, Page, Pie

logger = logging.getLogger(__name__)


def get_xaxis_days(days=60):
    """
    获取 X 坐标，按天。取两个月数据
    """
    xaxis_days = []
    for i in range(0, days):
        xaxis_days.append(time.strftime("%Y%m%d", time.localtime(time.time() - i * 86400)))
    xaxis_days.sort()
    return xaxis_days


def uv_line_chart() -> Line:
    """
    UV折线图，包括总UV、新用户UV
    """
    xaxis = get_xaxis_days()

    uv_all_redis_keys = [settings.REDIS_UV_ALL_KEY % day for day in xaxis]
    uv_new_redis_keys = [settings.REDIS_UV_NEW_KEY % day for day in xaxis]

    uv_all = R.mget(*uv_all_redis_keys)
    uv_new = R.mget(*uv_new_redis_keys)

    line = (
        Line()
        .add_xaxis(xaxis)
        .add_yaxis("总用户数", uv_all, is_connect_nones=True)
        .add_yaxis("新用户数", uv_new, is_connect_nones=True, color="#6950a1")
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


def refer_pie_chart() -> Pie:
    refer_hosts = list(R.smembers(settings.REDIS_REFER_ALL_KEY))
    refer_host_pv_keys = [settings.REDIS_REFER_PV_KEY % host for host in refer_hosts]

    c = (
        Pie()
        .add("", [list(z) for z in zip(refer_hosts, R.mget(*refer_host_pv_keys))])
        .set_global_opts(title_opts=options.TitleOpts(title="Referer来源占比"))
        .set_series_opts(label_opts=options.LabelOpts(formatter="{b}: {c}"))
        .dump_options()
    )
    return c


def get_uv_chart_data(request):
    return JsonResponse(json.loads(uv_line_chart()))


def get_refer_pie_data(request):
    return JsonResponse(json.loads(refer_pie_chart()))


def dashboard(request):
    return render(request, 'dashboard/index.html')
