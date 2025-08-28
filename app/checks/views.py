from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseNotFound
from django.db.models import Q
from .models import CheckRecord, PersonalLink
from datetime import date, timedelta, datetime, time
from mail.models import AccessToken


def root(request):
    return redirect("check")

# def check_page(request):
#     start = request.GET.get("start") or ""
#     end = request.GET.get("end") or ""
#     user = request.GET.get("user") or ""

#     q = Q()
#     if start:
#         q &= Q(date__gte=start)
#     if end:
#         q &= Q(date__lte=end)
#     if user:
#         q &= Q(user=user)

#     results = list(CheckRecord.objects.filter(q).order_by("-date","-time"))
#     total = len(results)
#     complete = len([r for r in results if r.status == "완료"])

#     return render(request, "check.html", {
#         "results": results,
#         "total": total,
#         "complete": complete,
#         "start": start,
#         "end": end,
#         "user": user,
#     })

def create_link(request):
    user_key = request.GET.get("user_key")
    if not user_key:
        return JsonResponse({"error": "user_key required"}, status=400)
    pl = PersonalLink.objects.create(user_key=user_key)
    return JsonResponse({"uuid": str(pl.uuid), "link": f"/p/{pl.uuid}"})

def personal_page(request, uuid):
    try:
        pl = PersonalLink.objects.get(uuid=uuid)
    except PersonalLink.DoesNotExist:
        return HttpResponseNotFound("<h3>잘못된 링크입니다.</h3>")
    return redirect(f"/check?user={pl.user_key}")



def check_view(request):
    start = request.GET.get("start") or ""
    end = request.GET.get("end") or ""
    user = request.GET.get("user") or ""

    q = Q()
    if start:
        q &= Q(date__gte=start)
    if end:
        q &= Q(date__lte=end)
    if user:
        q &= Q(user=user)

    today = date.today()
    last_monday = today - timedelta(days=today.isoweekday()+6)
    last_sunday = last_monday+timedelta(days=6)

    records = CheckRecord.objects.filter(date__range=[last_monday, last_sunday]).filter(q)

    # 평일 21~06시 / 주말 24시간 필터
    filtered_ids = []
    for r in records: 
        dt = datetime.combine(r.date, r.time)
        weekday = dt.weekday()
        if weekday < 5: 
            if dt.time() >= time(21,0) or dt.time() < time(6,0):
                filtered_ids.append(r.id)
        else:
            filtered_ids.append(r.id)

    weekly_records = records.filter(id__in=filtered_ids)

    # 날짜, 카테고리 정의
    dates = [last_monday + timedelta(days=i) for i in range(7)]
    date_strs = [d.strftime("%Y-%m-%d") for d in dates]

    categories = ["ssh","su","sftp","window"]
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

    context = {
        "results": weekly_records,
        "pivot": pivot,
        "dates": date_strs,
        "category_labels": category_labels,
        "complete": weekly_records.filter(appeal_done=True).count(),
        "total": weekly_records.count(),
        "last_monday": last_monday,
        "last_sunday": last_sunday,
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

    # 2. user 기반으로 기존 check_view 로직 재사용
    today = date.today()
    last_monday = today - timedelta(days=today.isoweekday() + 6)
    last_sunday = last_monday + timedelta(days=6)

    q = Q(user=user)

    records = CheckRecord.objects.filter(date__range=[last_monday, last_sunday]).filter(q)

    # 야간/주말 필터링
    filtered_ids = []
    for r in records:
        dt = datetime.combine(r.date, r.time)
        weekday = dt.weekday()
        if weekday < 5:
            if dt.time() >= time(21,0) or dt.time() < time(6,0):
                filtered_ids.append(r.id)
        else:
            filtered_ids.append(r.id)

    weekly_records = records.filter(id__in=filtered_ids)

    # pivot 집계 (원래 check_view 코드 그대로)
    dates = [last_monday + timedelta(days=i) for i in range(7)]
    date_strs = [d.strftime("%Y-%m-%d") for d in dates]

    categories = ["ssh","su","sftp","window"]
    category_labels = {
        "ssh": "SSH 접속 로그",
        "su": "SU 접속 로그",
        "sftp": "SFTP 로그",
        "window": "Window 로그",
    }

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

    context = {
        "results": weekly_records,
        "pivot": pivot,
        "dates": date_strs,
        "category_labels": category_labels,
        "complete": weekly_records.filter(appeal_done=True).count(),
        "total": weekly_records.count(),
        "last_monday": last_monday,
        "last_sunday": last_sunday,
        "user": user,  
    }

    return render(request, "check_token.html", context)



