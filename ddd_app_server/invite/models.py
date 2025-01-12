from django.db import models
from django.contrib.auth.models import User


class InviteCode(models.Model):
    INVITE_TYPE_CHOICES = [
        ('member', 'Member'),
        ('moderator', 'Moderator'),
    ]

    code = models.CharField(max_length=255, unique=True)
    invite_type = models.CharField(max_length=10, choices=INVITE_TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_invite_codes')

    def __str__(self):
        return self.code

