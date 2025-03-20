from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from invite.models import InviteCode


class Profile(models.Model):
    # user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    invite_code = models.ForeignKey(InviteCode, on_delete=models.SET_NULL, null=True, blank=True, related_name='profiles')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

    class Meta:
        ordering = ['-created_at']
