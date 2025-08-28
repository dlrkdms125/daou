import uuid
from django.db import models

class AccessToken(models.Model):
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    user = models.CharField(max_length=100)  
    created_at = models.DateTimeField(auto_now_add=True)
    expired_at = models.DateTimeField(null=True, blank=True)


def create_access_token(user: str):
    token_obj = AccessToken.objects.create(user=user)
    return f"http://127.0.0.1:8000/check/{token_obj.token}"

