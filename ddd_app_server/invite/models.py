from django.db import models
from django.contrib.auth.models import User
from datetime import timezone

class InviteCode(models.Model):
    INVITE_TYPE_CHOICES = [
        ('member', '멤버'),
        ('moderator', '운영진'),
    ]

    code = models.CharField(max_length=255, unique=True)
    invite_type = models.CharField(max_length=10, choices=INVITE_TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_invite_codes')
    expire_time = models.DateTimeField()
    one_time_use = models.BooleanField(default=False)

    def __str__(self):
        return self.code

    @property
    def is_expired(self):
        return self.expire_time and self.expire_time < timezone.now()
