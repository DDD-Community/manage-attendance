import uuid
from django.db import models
from django.contrib.auth.models import User
# Create your models here.

# QR 로그 모델
class QRLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='qr_logs')
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    decoded_at = models.DateTimeField(null=True, blank=True)
