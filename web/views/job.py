#
# from web.models import *
# from web.utils import get_client_ip, valid_dvc_req
# from django.conf import settings
# from django.http import HttpResponseNotFound, HttpResponseForbidden, JsonResponse
# import logging
# import gzip
# import json
# import django_rq
# from web.tasks import handle_job_async
#
# logger = logging.getLogger(__name__)
#
#
# def get_one_job(request):
#     dvc_id, dvc_type, dvc_ext, sign = request.POST['dvc_id'], request.POST['dvc_type'], request.POST['dvc_ext'], \
#                                       request.POST['sign']
#     dvc_ip = get_client_ip(request)
#
#     if not valid_dvc_req(dvc_id, dvc_type, sign):
#         logger.warning(f"设备请求校验失败：`{dvc_id}`{dvc_type}`{sign}")
#         return HttpResponseForbidden("")
#
#     try:
#         job = Job.objects.filter(status=0).order_by('id')[0]
#     except IndexError:
#         return HttpResponseNotFound("")
#
#     # TODO 用户设备处理
#     job.status = 1
#     job.dvc_id = dvc_id
#     job.dvc_type = dvc_type
#     job.dvc_ext = dvc_ext
#     job.dvc_ip = dvc_ip
#
#     job.save()
#     sleep = settings.ROBOT_DVC_CNF[dvc_id] if settings.ROBOT_DVC_CNF.get(dvc_id) else (60, 600)
#
#     return JsonResponse({"id": job.id, "url": job.url, "sleep": sleep})
#
#
# def giveback_job(request):
#     """
#     最多交还 3 次
#     """
#     job_id, job_url = request.POST['id'], request.POST['url']
#     job = Job.objects.get(pk=job_id, status=1)
#
#     if job.url == job_url:
#         job.giveback += 1
#         job.remark += f'{job.dvc_id},'
#
#         if job.giveback >= 2:
#             job.status = 5
#         else:
#             job.status = 0
#         job.save()
#
#         return JsonResponse({})
#
#     return HttpResponseForbidden("")
#
#
# def finish_job(request):
#     if request.headers.get('Content-Encoding') == 'gzip':
#         try:
#             body = json.loads(gzip.decompress(request.body).decode('utf8'))
#             job_id, job_url, rsp, rsp_url = body['id'], body['url'], body['rsp'], body['rsp_url']
#         except:
#             logger.warning("压缩请求处理异常！")
#             return HttpResponseForbidden("")
#     else:
#         job_id, job_url, rsp, rsp_url = request.POST['id'], request.POST['url'], request.POST['rsp'], \
#                                         request.POST['rsp_url']
#
#     # 更新状态
#     try:
#         Job.objects.filter(pk=int(job_id), status__in=(1, 3, 5)).update(status=8)
#     except Exception as e:
#         logger.warning(f"任务状态变更出现异常：`{e}`{job_id}")
#
#     # 最多保存 6 小时
#     django_rq.enqueue(handle_job_async, job_id, job_url, rsp, rsp_url, result_ttl=1, ttl=6*3600, job_timeout=300,
#                       failure_ttl=86400)
#
#     return JsonResponse({})
