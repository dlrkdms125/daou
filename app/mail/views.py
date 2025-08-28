# mail/views.py
from django.http import JsonResponse
from .utils import send_access_mail

# mail/views.py
from django.http import JsonResponse
from .utils import send_access_mail

def send_mail_view(request):
    try:
        # kaeunlee 유저에게 토큰 포함된 메일 보내기
        send_access_mail("kaeunlee", "mangoade100g@gmail.com")
        return JsonResponse({"status": "메일 발송 성공"})
    except Exception as e:
        return JsonResponse({"status": "에러", "message": str(e)})