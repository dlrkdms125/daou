from apscheduler.schedulers.background import BackgroundScheduler
from django.conf import settings

def start_if_enabled():
    if not settings.SCHEDULER_ENABLED:
        print("sheduler disabled")
        return
    from checks.tasks import fetch_from_es
    sch = BackgroundScheduler(timezone=settings.TIME_ZONE)
    sch.add_job(
        fetch_from_es,
        "interval",
        seconds=settings.FETCH_INTERVAL_SECONDS,
        id="fetch_from_es_job",
        replace_existing=True,  
        max_instances=1,
        coalesce=True,
    )
    sch.start()
    print(f"Scheduler started, interval={settings.FETCH_INTERVAL_SECONDS}")
