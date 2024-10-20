import uuid
from django.db import models
from django.contrib.auth.models import User


class InviteCode(models.Model):
    INVITE_TYPE_CHOICES = [
        ('normal', 'Normal'),
        ('moderator', 'Moderator'),
    ]

    code = models.CharField(max_length=255, unique=True)
    invite_type = models.CharField(max_length=10, choices=INVITE_TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_invite_codes')

    def __str__(self):
        return self.code


class Member(models.Model):
    # Connected with Django User (one-to-one relationship)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='member')  # Django's User model
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=255)
    team = models.CharField(max_length=255)
    invite_code = models.OneToOneField(InviteCode, on_delete=models.SET_NULL, null=True, related_name='member')  # Each member has one invite code
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class MemberAttendance(models.Model):
    member = models.OneToOneField(Member, on_delete=models.CASCADE, related_name='attendance')
    total_attendance = models.IntegerField()
    late_count = models.IntegerField()
    absent_count = models.IntegerField()

    def __str__(self):
        return f"{self.member.name}'s Attendance"
