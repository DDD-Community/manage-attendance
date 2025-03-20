# schedules/models.py
import uuid
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

class Schedule(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    # Future: Add assigned_users field for user assignment
    # assigned_users = models.ManyToManyField(User, related_name='assigned_schedules', blank=True)

    def __str__(self):
        return self.title

    def create_attendances_for_all_users(self):
        """Create attendance records for all users"""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        users = User.objects.filter(groups__name='member')
        for user in users:
            Attendance.objects.get_or_create(
                user=user,
                schedule=self,
                defaults={'status': 'tbd'}
            )

@receiver(post_save, sender=Schedule)
def create_attendances(sender, instance, created, **kwargs):
    if created:
        instance.create_attendances_for_all_users()

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
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendances')
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='attendances')
    status = models.CharField(max_length=10, choices=ATTENDANCE_STATUS_CHOICES, default='tbd')
    attendance_time = models.DateTimeField(null=True, blank=True)
    method = models.CharField(max_length=10, choices=METHOD_CHOICES, null=True, blank=True)
    note = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ['user', 'schedule']
        ordering = ['-schedule__start_time']

    def __str__(self):
        return f"{self.user} - {self.schedule} ({self.status})"
