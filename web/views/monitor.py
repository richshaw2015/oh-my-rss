from django.http import HttpResponse
from web.models import *
from web.utils import R
import subprocess


def heart_beat(request):
    """
    redis, database, process, disk size
    """
    try:
        key, value = 'HEARTBEAT', '$'*10*1024
        assert R.set(key, value, 1)
        assert R.get(key) == value
    except:
        return HttpResponse("FAIL: Redis")

    try:
        assert User.objects.all().count() > 0
    except:
        return HttpResponse("FAIL: Database")

    running_process = subprocess.getoutput("ps x")

    try:
        assert 2 == running_process.count('ohmyrss.wsgi:application')
    except:
        return HttpResponse("FAIL: ohmyrss.wsgi:application")

    disk_usage = subprocess.getoutput("df -h |grep '/dev/' | awk '{print $5}' | cut -f 1 -d '%' |sort -nr |head -n1")

    try:
        assert 0 < int(disk_usage.strip()) < 85
    except:
        return HttpResponse(f"FAIL: Disk size {disk_usage}")

    disk_inode = subprocess.getoutput("df -i |grep '/dev/' | awk '{print $5}' | cut -f 1 -d '%' |sort -nr |head -n1")

    try:
        assert 0 < int(disk_inode.strip()) < 90
    except:
        return HttpResponse(f"FAIL: Disk inode {disk_inode}")

    return HttpResponse("OK")
