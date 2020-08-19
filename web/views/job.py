
from web.models import *
from web.utils import get_client_ip, valid_dvc_req
from django.conf import settings
from django.http import HttpResponseNotFound, HttpResponseForbidden, JsonResponse
import logging
import gzip
import json
from web.rssparser.mpwx import parse_list_page, parse_detail_page

logger = logging.getLogger(__name__)


def get_one_job(request):
    dvc_id, dvc_type, dvc_ext, sign = request.POST['dvc_id'], request.POST['dvc_type'], request.POST['dvc_ext'], \
                                      request.POST['sign']
    dvc_ip = get_client_ip(request)

    if not valid_dvc_req(dvc_id, dvc_type, sign):
        logger.warning(f"设备请求校验失败：`{dvc_id}`{dvc_type}`{sign}")
        return HttpResponseForbidden("")

    try:
        job = Job.objects.filter(status=0).order_by('id')[0]
    except IndexError:
        return HttpResponseNotFound("")

    # TODO 用户设备处理
    job.status = 1
    job.dvc_id = dvc_id
    job.dvc_type = dvc_type
    job.dvc_ext = dvc_ext
    job.dvc_ip = dvc_ip

    job.save()

    if settings.ROBOT_DVC_CNF.get(dvc_id):
        return JsonResponse({"id": job.id, "url": job.url, "sleep": settings.ROBOT_DVC_CNF[dvc_id]})
    else:
        return JsonResponse({"id": job.id, "url": job.url})


def giveback_job(request):
    """
    最多交还 3 次
    """
    job_id, job_url = request.POST['id'], request.POST['url']
    job = Job.objects.get(pk=job_id, status=1)

    if job.url == job_url:
        job.giveback += 1
        job.remark += f'{job.dvc_id},'

        if job.giveback >= 3:
            job.status = 5
        else:
            job.status = 0
        job.save()

        return JsonResponse({})

    return HttpResponseForbidden("")


def finish_job(request):
    if request.headers.get('Content-Encoding') == 'gzip':
        try:
            body = json.loads(gzip.decompress(request.body).decode('utf8'))
            job_id, job_url, rsp, rsp_url = body['id'], body['url'], body['rsp'], body['rsp_url']
        except:
            logger.warning("压缩请求处理异常！")
            return HttpResponseForbidden("")
    else:
        job_id, job_url, rsp, rsp_url = request.POST['id'], request.POST['url'], request.POST['rsp'], \
                                        request.POST['rsp_url']

    job, status = Job.objects.get(pk=job_id, status=1), -1

    if job.url == job_url:
        job.rsp = rsp
        job.rsp_url = rsp_url

        if job.action in (10, 11, 12, 13):
            status = parse_list_page(job)
        elif job.action in (20, 21, 22, 23):
            status = parse_detail_page(job)
        else:
            logger.warning(f"未知的任务类型：`{job.action}")

        job.status = status
        if status == 2:
            job.rsp = ''

        job.save()

        return JsonResponse({})
    else:
        logger.warning(f"任务不匹配：`{job.id}`{job.url}`{job_url}")
        return HttpResponseForbidden("")
