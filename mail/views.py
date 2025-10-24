# mail/views.py
from django.http import JsonResponse
from .utils import send_access_mail


def send_mail_view(request):
    try:
        user = "kaeunlee"  
        UserAccessLog.objects.create(user=user)
        return JsonResponse({"status": "접속 기록 저장 성공"})
    except Exception as e:
        return JsonResponse({"status": "에러", "message": str(e)})