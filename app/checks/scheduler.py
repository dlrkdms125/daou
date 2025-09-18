from apscheduler.schedulers.background import BackgroundScheduler
from django.conf import settings

# APIScheduler를 이용해서 매일 자정 실행되는 작업을 등록하는 함수
def start_if_enabled():
    if not settings.SCHEDULER_ENABLED:  # settings.py에 SCHEDULER_ENABLED=True 설정이 되어 있어야만 동작함
        print("scheduler disabled")
        return

    from checks.tasks import fetch_from_es
    from mail.tasks import send_scheduled_mails   # 👈 메일 발송 함수 import

    # BackgroundScheduler 객체를 생성함
    sch = BackgroundScheduler(timezone=settings.TIME_ZONE)

    # 1. 전날 ES → PostgreSQL 이관 (자정)
    sch.add_job(
        fetch_from_es,
        "cron",
        hour=0, minute=0,
        id="fetch_from_es_job",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )

    # 2. 전날 접속 로그가 있으면 메일 발송 (매일 18시)
    sch.add_job(
        send_scheduled_mails,
        "cron",
        hour=17, minute=19,
        id="send_mail_job",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )

    sch.start()
    print("Scheduler started: fetch_from_es at 00:00, send_scheduled_mails at 18:00")
