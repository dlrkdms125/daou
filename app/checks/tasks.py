
from celery import shared_task
from django.conf import settings
from elasticsearch import Elasticsearch
from django.utils import timezone
from .models import CheckRecord
import datetime as dt
import random

@shared_task
def pull_or_seed():
    if settings.DEMO_MODE:
        seed_demo(3)
    else:
        pull_from_es()

def pull_from_es():
    es = Elasticsearch(settings.ES_HOST, verify_certs=False)
    try:
        res = es.search(
            index=settings.ES_INDEX,
            query={"range": {"@timestamp": {"gte": "now-1m", "lte": "now"}}},
            size=1000,
        )
        hits = [h.get("_source", {}) for h in res.get("hits", {}).get("hits", [])]
    except Exception:
        hits = []
    for d in hits:
        now = dt.datetime.now()
        date = d.get("date") or now.strftime("%Y-%m-%d")
        time = d.get("time") or now.strftime("%H:%M:%S")
        item = d.get("item") or d.get("event", "점검")
        server = d.get("server", "unknown")
        user = d.get("user", d.get("account", "unknown"))
        ip = d.get("ip", "0.0.0.0")
        switch_su = d.get("switch_su", "-")
        sftp_file = d.get("sftp_file", "-")
        reason = d.get("reason", "")
        appeal_done = bool(d.get("appeal_done", False))
        status = d.get("status", "미입력")

        CheckRecord.objects.create(
            date=date, time=time, item=item, server=server, user=user, ip=ip,
            switch_su=switch_su, sftp_file=sftp_file, reason=reason,
            appeal_done=appeal_done, status=status
        )

def seed_demo(n: int = 5):
    now = dt.datetime.now()
    for _ in range(n):
        t = now - dt.timedelta(seconds=random.randint(0, 59))
        CheckRecord.objects.create(
            date=t.strftime("%Y-%m-%d"),
            time=t.strftime("%H:%M:%S"),
            item=random.choice(["계정접속", "파일전송", "권한승격"]),
            server=random.choice(["app-1", "db-1", "cache-1"]),
            user=random.choice(["gaeun", "admin", "guest"]),
            ip=f"192.168.0.{random.randint(1,254)}",
            switch_su=random.choice(["-", "su", "sudo"]),
            sftp_file=random.choice(["-", "/tmp/a.txt", "/var/log/app.log"]),
            reason="",
            appeal_done=random.choice([False, False, True]),
            status=random.choice(["미입력", "완료대기"]),
        )
