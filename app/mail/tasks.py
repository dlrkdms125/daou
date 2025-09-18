from django.utils.timezone import now
from datetime import datetime, timedelta, time
from checks.models import CheckRecord
from .views import send_access_mail   # utils.py로 빼는 게 더 깔끔

def send_scheduled_mails():
    today = now().date()
    yesterday = today - timedelta(days=1)

    # 전날 00:00~05:59
    logs1 = CheckRecord.objects.filter(
        date=yesterday,
        time__range=(time(0, 0), time(5, 59, 59))
    )
    # 전날 21:00~23:59
    logs2 = CheckRecord.objects.filter(
        date=yesterday,
        time__range=(time(21, 0), time(23, 59, 59))
    )

    logs = logs1 | logs2

    users = logs.values_list("user", flat=True).distinct()
    users = [u.strip().lower() for u in users if u]


    if not users:
        print("메일 발송 대상 없음")
    else:
        print(f"메일 발송 대상: {list(users)}")

    for user in users:
        send_access_mail(user, "mangoade100g@gmail.com")

