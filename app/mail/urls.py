# mail/urls.py
from django.urls import path
from .views import send_mail_view
from .models import create_access_token 

urlpatterns = [
    path("send-mail/", send_mail_view, name="send_mail"),
    
]
