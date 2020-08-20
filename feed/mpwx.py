
"""
分布式爬虫处理；包括取任务、执行任务、上报结果
"""

import requests
from requests.adapters import HTTPAdapter
import platform
import time
import json
import random
import logging
import gzip
import hashlib

logging.basicConfig(level=logging.INFO,
                    filename='sys.log',
                    filemode='a',
                    format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'
                    )

API_URL = 'https://ohmyrss.com'
# API_URL = 'http://127.0.0.1:8080'

DVC_ID = platform.node()
DVC_TYPE = 'robot'
DVC_EXT = {
    'pf': platform.platform(),
    'sys': platform.system(),
    'sysver': platform.version(),
    'ver': '1.2',
    'lat': '',
    'lon': '',
    'model': '',
}

UAS = [
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/74.0.835.163 Safari/535.1',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0) Gecko/20100101 Firefox/78.0',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.50 (KHTML, like Gecko) Version/13.0 Safari/534.50',
    'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Win64; x64; Trident/5.0)',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Edg/83.0.478.54',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/605.1 (KHTML, like Gecko) Version/13.0.3 Safari/605.1',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1',
    'Mozilla/5.0 (CrKey armv7l 1.5.16041) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.0 Safari/537.36',
]


def md5(src):
    return hashlib.md5(src.encode('utf8')).hexdigest()


def current_day():
    return time.strftime("%Y%m%d", time.localtime(time.time()))


def get_a_job():
    try:
        rsp = requests.post(API_URL + '/api/job/get', data={
            "dvc_id": DVC_ID,
            "dvc_type": DVC_TYPE,
            "sign": md5(f"{DVC_ID}{DVC_TYPE}{current_day()}"),
            "dvc_ext": json.dumps(DVC_EXT)
        }, timeout=30)

        if rsp.ok:
            return rsp.json()
    except:
        logging.warning("获取任务出现异常！")

    return None


def handle_job(job):
    try:
        headers = {'User-Agent': random.choice(UAS), 'Referer': 'https://www.google.com'}
        rsp = requests.get(job['url'], headers=headers, timeout=30)

        if rsp.ok:
            job['rsp'] = rsp.text
            job['rsp_url'] = rsp.url
            return True
        else:
            logging.warning(f"执行任务失败：`{job}`{rsp.status_code}")
    except:
        logging.warning(f"执行任务出现异常：`{job}")

    return False


def giveback_job(job):
    try:
        rsp = requests.post(API_URL + '/api/job/giveback', data={
            "id": job['id'],
            "url": job['url'],
        }, timeout=30)

        if rsp.ok:
            return True
        else:
            logging.warning(f"交还任务失败：`{job}")
    except:
        logging.warning(f"交还任务出现异常：`{job}")

    return False


def finish_job(job):
    # 这里做两次重试，确保数据传输可靠性；并做请求体压缩
    s = requests.Session()
    s.mount('http://', HTTPAdapter(max_retries=2))
    s.mount('https://', HTTPAdapter(max_retries=2))

    try:
        body = json.dumps({
            "id": job['id'],
            "url": job['url'],
            "rsp": job['rsp'],
            "rsp_url": job['rsp_url'],
        })
        body = gzip.compress(bytes(body, 'utf8'))
        rsp = s.post(API_URL + '/api/job/finish', data=body, timeout=30, headers={'Content-Encoding': 'gzip'})

        if rsp.ok:
            logging.info(f"任务执行成功：`{job['id']}`{job['url']}")
            return True
        else:
            logging.warning(f"结束任务失败：`{job['id']}`{job['url']}")
    except:
        logging.warning(f"结束任务出现异常：`{job['id']}`{job['url']}")

    return False


# 间隔时间，受服务器控制
idle_sleep = 180
busy_sleep = 20


while True:
    job = get_a_job()

    if job is None:
        time.sleep(idle_sleep)
    else:
        if job.get('sleep'):
            busy_sleep = job['sleep'][0]
            idle_sleep = job['sleep'][1]

        # 开始处理，失败则交还
        if not handle_job(job):
            giveback_job(job)
        else:
            finish_job(job)
            time.sleep(busy_sleep)