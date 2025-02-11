from django.db import models
from django.contrib.auth.models import User
from invite.models import InviteCode


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    invite_code = models.ForeignKey(InviteCode, on_delete=models.SET_NULL, null=True, related_name='Profiles')  # Each invite code can be used by multiple members
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
