from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver
from schedules.models import Schedule
from attendances.models import Attendance
from django.contrib.auth.models import User, Group


@receiver(m2m_changed, sender=User.groups.through)
def sync_attendance_on_user_groups_change(sender, instance, action, pk_set, **kwargs):
    """
    Handles creation/deletion of attendance records when a user's group membership changes.
    - instance: The User object whose groups changed.
    - pk_set: A set of Group primary keys that were added/removed.
    """
    user = instance

    if action == 'post_add':
        schedules_for_new_groups = Schedule.objects.filter(group_id__in=pk_set).distinct()

        attendance_to_create = []
        for schedule in schedules_for_new_groups:
            is_staff = (user.is_staff or user.groups.filter(name="moderator").exists())
            if not is_staff:
                attendance_to_create.append(Attendance(user=user, schedule=schedule, status='tbd'))
        
        if attendance_to_create:
            Attendance.objects.bulk_create(attendance_to_create, ignore_conflicts=True)

    elif action == 'post_remove':
        Attendance.objects.filter(user=user, schedule__group_id__in=pk_set).delete()


@receiver(post_save, sender=Schedule)
def sync_attendance_on_schedule_group_change(sender, instance, created, **kwargs):
    """
    Handles creation/deletion of attendance records when a Schedule's group changes,
    or when a Schedule is created with an group.
    - instance: The Schedule object that was saved.
    - created: Boolean, True if a new record was created.
    """
    schedule = instance

    # Get users who currently have an attendance record for this schedule
    current_users_with_attendance_qs = User.objects.filter(
        attendances__schedule=schedule
    ).distinct()

    users_in_new_group_qs = User.objects.none()
    if schedule.group:
        users_in_new_group_qs = schedule.group.user_set.all()

    # 1. Determine users whose attendance should be removed
    users_to_remove_attendance = current_users_with_attendance_qs.exclude(
        pk__in=users_in_new_group_qs.values_list('pk', flat=True)
    )
    if users_to_remove_attendance.exists():
        Attendance.objects.filter(schedule=schedule, user__in=users_to_remove_attendance).delete()

    # 2. Determine users for whom attendance should be created
    if schedule.group:
        users_to_add_attendance = users_in_new_group_qs.exclude(
            pk__in=current_users_with_attendance_qs.values_list('pk', flat=True)
        )
        
        attendance_to_create = []
        for user in users_to_add_attendance:
            is_staff = (user.is_staff or user.groups.filter(name="moderator").exists())
            if not is_staff:
                attendance_to_create.append(Attendance(user=user, schedule=schedule, status='tbd'))
        
        if attendance_to_create:
            Attendance.objects.bulk_create(attendance_to_create, ignore_conflicts=True)