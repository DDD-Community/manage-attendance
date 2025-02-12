# schedules/models.py
import uuid
from django.db import models
from django.contrib.auth.models import User

class Schedule(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Attendance(models.Model):
    ATTENDANCE_STATUS_CHOICES = (
        ('tbd', '미정'),
        ('present', '출석'),
        ('late', '지각'),
        ('absent', '결석'),
        ('exception', '예외'),
    )
    METHOD_CHOICES = (
        ('qr', 'QR출석'),
        ('manual', '수동출석'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='attendances')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    attendance_status = models.CharField(max_length=10, choices=ATTENDANCE_STATUS_CHOICES, default='tbd')
    method = models.CharField(max_length=10, choices=METHOD_CHOICES, null=True, blank=True)
    note = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user} - {self.schedule} ({self.attendance_status})"
