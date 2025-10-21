from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseNotFound
from django.db.models import Q
from .models import CheckRecord, PersonalLink
from datetime import date, timedelta, datetime, time
from mail.models import AccessToken


def root(request): # / 로 접속하면 자동으로 /check 페이지로 리다이렉트
    return redirect("check")

def create_link(request):
    user_key = request.GET.get("user_key")
    if not user_key:
        return JsonResponse({"error": "user_key required"}, status=400)
    pl = PersonalLink.objects.create(user_key=user_key) # user_key가 있으면 PersonalLink 객체 생성: uuid발급
    return JsonResponse({"uuid": str(pl.uuid), "link": f"/p/{pl.uuid}"})

def personal_page(request, uuid):
    try:
        pl = PersonalLink.objects.get(uuid=uuid)
    except PersonalLink.DoesNotExist:
        return HttpResponseNotFound("<h3>잘못된 링크입니다.</h3>")
    return redirect(f"/check?user={pl.user_key}") # check_view 로직 재사용함

from django.shortcuts import render
from django.db.models import Q
from datetime import date, timedelta, datetime, time
from .models import CheckRecord

def check_view(request):
    start = request.GET.get("start") or ""
    end = request.GET.get("end") or ""
    user = request.GET.get("user") or ""

    # 조건이 바뀔 수 있어서 Q 객체 사용
    q = Q()
    if start:
        q &= Q(date__gte=start)
    if end:
        q &= Q(date__lte=end)
    if user:
        q &= Q(user=user)

    today = date.today()
    last_monday = today - timedelta(days=today.isoweekday() + 6)
    last_sunday = last_monday + timedelta(days=6)

    # ======================
    # 지난주 요약용 데이터
    # ======================
    records = CheckRecord.objects.filter(date__range=[last_monday, last_sunday]).filter(q)

    # 평일 21~06시 / 주말 24시간 필터
    filtered_ids = []
    for r in records:
        dt = datetime.combine(r.date, r.time)
        weekday = dt.weekday()
        if weekday < 5:
            if dt.time() >= time(21, 0) or dt.time() < time(6, 0):
                filtered_ids.append(r.id)
        else:
            filtered_ids.append(r.id)

    weekly_records = records.filter(id__in=filtered_ids)

    # 날짜, 카테고리 정의
    dates = [last_monday + timedelta(days=i) for i in range(7)]
    date_strs = [d.strftime("%Y-%m-%d") for d in dates]

    categories = ["ssh", "su", "sftp", "window"]
    category_labels = {
        "ssh": "SSH 접속 로그",
        "su": "SU 접속 로그",
        "sftp": "SFTP 로그",
        "window": "Window 로그",
    }

    # pivot 집계
    pivot = {cat: {d: 0 for d in date_strs} for cat in categories}
    for cat in categories:
        pivot[cat]["total"] = 0

    for r in weekly_records:
        d = r.date.strftime("%Y-%m-%d")
        if r.reason == "ssh":
            pivot["ssh"][d] += 1
            pivot["ssh"]["total"] += 1
        if r.reason == "su":
            pivot["su"][d] += 1
            pivot["su"]["total"] += 1
        if getattr(r, "sftp_file", "-") and r.sftp_file != "-":
            pivot["sftp"][d] += 1
            pivot["sftp"]["total"] += 1
        if r.reason == "window":
            pivot["window"][d] += 1
            pivot["window"]["total"] += 1

    # ======================
    # 전체 데이터 (밑에 테이블)
    # ======================
    all_records = CheckRecord.objects.filter(q).order_by("-date", "-time")

    context = {
        # 위쪽 표: 지난주 요약
        "pivot": pivot,
        "dates": date_strs,
        "category_labels": category_labels,
        "complete": weekly_records.filter(appeal_done=True).count(),
        "total": weekly_records.count(),
        "last_monday": last_monday,
        "last_sunday": last_sunday,

        # 아래쪽 표: 전체 데이터
        "results": all_records,

        # 검색 파라미터
        "start": start,
        "end": end,
        "user": user,
    }

    try:
        return render(request, "check.html", context)
    except Exception as e:
        import traceback
        print("에러 발생:", e)
        traceback.print_exc()
        from django.http import HttpResponse
        return HttpResponse(f"Error: {e}", status=500)



def check_by_token(request, token):
    # 1. 토큰 찾기
    access_token = get_object_or_404(AccessToken, token=token)
    user = access_token.user

    # 2. 전날 날짜 계산
    yesterday = date.today() - timedelta(days=1)

    # 3. 시간대 범위 정의 (00:00~05:59, 21:00~23:59)
    start1, end1 = time(0, 0), time(5, 59, 59)
    start2, end2 = time(21, 0), time(23, 59, 59)

    # 4. 조건 필터링
    q = Q(user=user, date=yesterday) & (
        Q(time__range=(start1, end1)) |
        Q(time__range=(start2, end2))
    )

    records = CheckRecord.objects.filter(q).order_by("date", "time")

    # 5. pivot 집계 (원래 로직 유지)
    categories = ["ssh", "su", "sftp", "window"]
    category_labels = {
        "ssh": "SSH 접속 로그",
        "su": "SU 접속 로그",
        "sftp": "SFTP 로그",
        "window": "Window 로그",
    }

    pivot = {cat: {str(yesterday): 0, "total": 0} for cat in categories}

    for r in records:
        d = r.date.strftime("%Y-%m-%d")
        if r.reason == "ssh":
            pivot["ssh"][d] += 1
            pivot["ssh"]["total"] += 1
        if r.reason == "su":
            pivot["su"][d] += 1
            pivot["su"]["total"] += 1
        if getattr(r, "sftp_file", "-") and r.sftp_file != "-":
            pivot["sftp"][d] += 1
            pivot["sftp"]["total"] += 1
        if r.reason == "window":
            pivot["window"][d] += 1
            pivot["window"]["total"] += 1

    context = {
        "results": records,
        "pivot": pivot,
        "dates": [yesterday.strftime("%Y-%m-%d")],
        "category_labels": category_labels,
        "complete": records.filter(appeal_done=True).count(),
        "total": records.count(),
        "yesterday": yesterday,
        "user": user,
    }

    return render(request, "check_token.html", context)




