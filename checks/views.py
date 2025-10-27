from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseNotFound
from django.db.models import Q
from .models import CheckRecord, PersonalLink
from datetime import date, timedelta, datetime, time
from mail.models import AccessToken
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST




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

from elasticsearch import Elasticsearch
from datetime import date, timedelta, datetime, time
from django.shortcuts import render
from django.http import HttpResponse


def check_view(request):
    # 검색 조건 파라미터
    start = request.GET.get("start") or ""
    end = request.GET.get("end") or ""
    user = request.GET.get("user") or ""

    # 지난주 날짜 계산
    today = date.today()
    last_monday = today - timedelta(days=today.isoweekday() + 6)
    last_sunday = last_monday + timedelta(days=6)

    try:
        # ==========================
        # [A] 위쪽 표: Elasticsearch
        # ==========================
        es = Elasticsearch("http://localhost:9200")

        must_conditions = [
            {"range": {"date": {"gte": last_monday.strftime("%Y-%m-%d"),
                                "lte": last_sunday.strftime("%Y-%m-%d")}}}
        ]
        if user:
            must_conditions.append({"term": {"user.keyword": user}})

        query = {
            "query": {"bool": {"must": must_conditions}},
            "size": 10000
        }

        res = es.search(index="checks_checkrecord", body=query)
        es_records = [hit["_source"] for hit in res["hits"]["hits"]]

        # pivot 집계
        categories = ["ssh", "su", "sftp", "window", "vdi"]
        category_labels = {
            "ssh": "SSH 접속 로그",
            "su": "SU 접속 로그",
            "sftp": "SFTP 로그",
            "window": "Window 로그",
            "vdi": "VDI 로그"
        }

        dates = [last_monday + timedelta(days=i) for i in range(7)]
        date_strs = [d.strftime("%Y-%m-%d") for d in dates]
        pivot = {cat: {d: 0 for d in date_strs} for cat in categories}
        for cat in categories:
            pivot[cat]["total"] = 0

        for r in es_records:
            d = r.get("date")
            if not d:
                continue
            reason = r.get("reason")
            if reason == "ssh":
                pivot["ssh"][d] += 1
                pivot["ssh"]["total"] += 1
            elif reason == "su":
                pivot["su"][d] += 1
                pivot["su"]["total"] += 1
            elif r.get("sftp_file") and r["sftp_file"] != "-":
                pivot["sftp"][d] += 1
                pivot["sftp"]["total"] += 1
            elif reason == "window":
                pivot["window"][d] += 1
                pivot["window"]["total"] += 1
            elif reason == "vdi":
                pivot["vdi"][d] += 1
                pivot["vdi"]["total"] += 1

        # ==========================
        # [B] 아래쪽 표: PostgreSQL
        # ==========================
        q = Q()
        if start:
            q &= Q(date__gte=start)
        if end:
            q &= Q(date__lte=end)
        if user:
            q &= Q(user=user)

        from .models import CheckRecord
        all_records = CheckRecord.objects.filter(q).order_by("-date", "-time")

        # ==========================
        # [C] 컨텍스트 구성
        # ==========================
        # context는 장고에서 템플릿(.html)로 데이터를 넘겨주는 딕셔너리
        context = {
            # 위쪽 표
            "pivot": pivot,
            "dates": date_strs,
            "category_labels": category_labels,
            "complete": sum(1 for r in es_records if r.get("appeal_done")),
            "total": len(es_records),
            "last_monday": last_monday,
            "last_sunday": last_sunday,

            # 아래쪽 표
            "results": all_records,
            "total": all_records.count(),

            # 검색 조건
            "start": start,
            "end": end,
            "user": user,
        }

        return render(request, "check.html", context)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return HttpResponse(f"<pre>{traceback.format_exc()}</pre>", status=500)


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
    categories = ["ssh", "su", "sftp", "window","vdi"]
    category_labels = {
        "ssh": "SSH 접속 로그",
        "su": "SU 접속 로그",
        "sftp": "SFTP 로그",
        "window": "Window 로그",
        "vdi": "VDI 로그"
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
        if r.reason == "vdi":
            pivot["vdi"][d] += 1
            pivot["vdi"]["vdi"] += 1

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

@csrf_exempt
@require_POST
def update_reason(request):
    record_id = request.POST.get("id")
    reason = request.POST.get("reason", "")[:200]
    try:
        record = CheckRecord.objects.get(id=record_id)
        record.reason = reason
        record.save()
        return JsonResponse({"success": True})
    except CheckRecord.DoesNotExist:
        return JsonResponse({"success": False, "error": "record not found"}, status=404)

