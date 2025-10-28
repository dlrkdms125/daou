import os
import django
from apscheduler.schedulers.background import BackgroundScheduler
from django.conf import settings
from .tasks import fetch_from_es

#  중복 실행 방지를 위한 전역 변수
_scheduler_started = False

def start_if_enabled():
    global _scheduler_started
    if _scheduler_started:
        print("[LOG] Scheduler already started, skipping.")
        return

    _scheduler_started = True

    if not settings.SCHEDULER_ENABLED:
        print("scheduler disabled")
        return
    # 스케줄러가 주기적으로 실행할 함수
    from checks.tasks import fetch_from_es
    from mail.tasks import send_scheduled_mails
    from checks.tasks import fetch_from_es, delete_old_records 

    # BackgroundScheduler 객체 생성(백그라운드에서 비동기적으로 동작)
    sch = BackgroundScheduler(timezone=settings.TIME_ZONE)

    sch.add_job(
        fetch_from_es,
        "cron",
        hour=14, minute=16,
        id="fetch_from_es_job",
        replace_existing=True, # 동일 ID의 job이 있으면 덮어쓰기
        max_instances=1, 
        coalesce=True, # 서버가 잠깐 멈췄다가 재시작된 경우, 밀린 job은 한번만 실행
    )

    sch.add_job(
        send_scheduled_mails,
        "cron",
        hour=14, minute=16,
        id="send_mail_job",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )

    sch.add_job(
        delete_old_records,
        "cron",
        hour=00, minute=00,
        id="delete_old_records_job",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )

    sch.start() # 스케줄러 실행
    print("[LOG] Scheduler started successfully.")
