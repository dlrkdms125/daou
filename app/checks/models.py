
from django.db import models
import uuid

class CheckRecord(models.Model):
    date = models.CharField(max_length=10, db_index=True)  # YYYY-MM-DD
    time = models.CharField(max_length=8)                  # HH:MM:SS
    item = models.CharField(max_length=100)                # 점검항목
    server = models.CharField(max_length=100)
    user = models.CharField(max_length=100)                # 접속자
    ip = models.CharField(max_length=45)
    switch_su = models.CharField(max_length=100)
    sftp_file = models.CharField(max_length=200)
    reason = models.TextField(blank=True, default="")
    appeal_done = models.BooleanField(default=False)       # 소명여부
    status = models.CharField(max_length=20, default="미입력")

class PersonalLink(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user_key = models.CharField(max_length=100, db_index=True)
