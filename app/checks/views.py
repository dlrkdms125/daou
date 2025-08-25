
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseNotFound
from django.db.models import Q
from .models import CheckRecord, PersonalLink

def root(request):
    return redirect("check")

def check_page(request):
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

    results = list(CheckRecord.objects.filter(q).order_by("-date","-time"))
    total = len(results)
    complete = len([r for r in results if r.status == "완료"])

    return render(request, "check.html", {
        "results": results,
        "total": total,
        "complete": complete,
        "start": start,
        "end": end,
        "user": user,
    })

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

def user_check_list(request, token):
    link = get_object_or_404(PersonalLink, token=token)
    username = link.user_key
    records = CheckRecord.objects.filter(user=username).order_by("-date", "-time")
    return render(request, "check.html", {"records": records, "username": username})
