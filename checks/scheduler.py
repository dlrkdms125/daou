from apscheduler.schedulers.background import BackgroundScheduler
from django.conf import settings

# ✅ 중복 실행 방지를 위한 전역 변수
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

    from checks.tasks import fetch_from_es
    from mail.tasks import send_scheduled_mails

    sch = BackgroundScheduler(timezone=settings.TIME_ZONE)

    sch.add_job(
        fetch_from_es,
        "cron",
        hour=0, minute=0,
        id="fetch_from_es_job",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )

    sch.add_job(
        send_scheduled_mails,
        "cron",
        hour=11, minute=00,
        id="send_mail_job",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )

    sch.start()
    print("[LOG] Scheduler started successfully.")
