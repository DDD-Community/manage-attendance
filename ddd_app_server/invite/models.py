from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

def one_week_from_now():
    return timezone.now() + timedelta(days=7)

class InviteCode(models.Model):
    INVITE_TYPE_CHOICES = [
        ('member', '멤버'),
        ('moderator', '운영진'),
    ]

    code = models.CharField(max_length=10, unique=True)
    invite_type = models.CharField(max_length=10, choices=INVITE_TYPE_CHOICES)
    used = models.BooleanField(default=False)
    expire_time = models.DateTimeField(default=one_week_from_now)  # Default 1 week
    one_time_use = models.BooleanField(default=True)  # Default True
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_invite_codes')

    def __str__(self):
        return self.code
