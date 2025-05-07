from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from .models import Schedule, Attendance
from django.contrib.auth.models import Group


@receiver(m2m_changed, sender=Schedule.assigned_users.through)
def sync_attendance_on_user_change(sender, instance, action, pk_set, **kwargs):
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
def sync_attendance_on_group_change(sender, instance, action, pk_set, **kwargs):
    if action == 'post_add':
        for group_id in pk_set:
            group = Group.objects.get(pk=group_id)
            for user in group.user_set.all():
                Attendance.objects.get_or_create(
                    user=user,
                    schedule=instance,
                    defaults={'status': 'tbd'}
                )
    elif action == 'post_remove':
        for group_id in pk_set:
            group = Group.objects.get(pk=group_id)
            Attendance.objects.filter(user__in=group.user_set.all(), schedule=instance).delete()
