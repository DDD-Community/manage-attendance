from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from .models import Schedule, Attendance
from django.contrib.auth.models import User, Group


@receiver(m2m_changed, sender=User.groups.through)
def sync_attendance_on_user_groups_change(sender, instance, action, pk_set, **kwargs):
    if action == 'post_add':
        schedules = Schedule.objects.filter(assigned_groups__in=pk_set).distinct()
        attendance_objects = [
            Attendance(user=instance, schedule=schedule, status='tbd')
            for schedule in schedules
        ]
        Attendance.objects.bulk_create(attendance_objects, ignore_conflicts=True)
    elif action == 'post_remove':
        Attendance.objects.filter(schedule__assigned_groups__in=pk_set, user=instance).delete()


@receiver(m2m_changed, sender=Schedule.assigned_users.through)
def sync_attendance_on_schedule_users_change(sender, instance, action, pk_set, **kwargs):
    if action == 'post_add':
        for user_id in pk_set:
            Attendance.objects.get_or_create(
                user_id=user_id,
                schedule=instance,
                defaults={'status': 'tbd'}
            )
    elif action == 'post_remove':
        Attendance.objects.filter(user_id__in=pk_set, schedule=instance).delete()


@receiver(m2m_changed, sender=Schedule.assigned_groups.through)
def sync_attendance_on_schedule_groups_change(sender, instance, action, pk_set, **kwargs):
    if action == 'post_add':
        groups = Group.objects.filter(pk__in=pk_set).prefetch_related('user_set')
        for group in groups:
            users = group.user_set.all()
            attendance_objects = [
                Attendance(user=user, schedule=instance, status='tbd')
                for user in users
            ]
            Attendance.objects.bulk_create(attendance_objects, ignore_conflicts=True)
    elif action == 'post_remove':
        groups = Group.objects.filter(pk__in=pk_set).prefetch_related('user_set')
        for group in groups:
            users = group.user_set.all()
            Attendance.objects.filter(user__in=users, schedule=instance).delete()
