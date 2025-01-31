import uuid
from django.db import models
from django.contrib.auth.models import User
from invite.models import InviteCode

class Tag(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Member(models.Model):
    # Connected with Django User (one-to-one relationship)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='member')  # Django's User model
    name = models.CharField(max_length=255)
    tags = models.ManyToManyField(Tag, related_name='members', blank=True)
    invite_code = models.OneToOneField(InviteCode, on_delete=models.SET_NULL, null=True, related_name='member')  # Each member has one invite code
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
