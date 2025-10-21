import uuid
from django.db import models
from datetime import timedelta
from django.utils import timezone

def get_expired_at():
    return timezone.now()+timedelta(weeks=2)

class AccessToken(models.Model):
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    user = models.CharField(max_length=100)  
    created_at = models.DateTimeField(auto_now_add=True)
    expired_at = models.DateTimeField(default=get_expired_at)

def create_access_token(user: str):
    user = user.strip().lower()  # 공백, 대소문자 차이 제거
    token_obj = AccessToken.objects.create(user=user)
    return f"http://127.0.0.1:8000/check/{token_obj.token}"


class UserAccessLog(models.Model):
    user = models.CharField(max_length=100)
    accessed_at = models.DateTimeField(auto_now_add=True)