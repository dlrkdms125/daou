from apscheduler.schedulers.background import BackgroundScheduler
from django.conf import settings

def start_if_enabled():
    if not settings.SCHEDULER_ENABLED:
        print("scheduler disabled")
        return

    from checks.tasks import fetch_from_es

    sch = BackgroundScheduler(timezone=settings.TIME_ZONE)
    sch.add_job(
        fetch_from_es,
        "cron",
        hour=0, minute=0,   # 매일 자정 00:00 실행
        id="fetch_from_es_job",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )
    sch.start()
    print("Scheduler started: runs daily at 00:00")

