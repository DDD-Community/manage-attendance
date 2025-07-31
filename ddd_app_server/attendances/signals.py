from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver
from schedules.models import Schedule
from attendances.models import Attendance
from django.contrib.auth.models import User

import pprint
import logging

logger = logging.getLogger(__name__)

def user_is_staff_or_moderator(user):
    """Helper to check if a user is staff or a moderator."""
    return user.is_staff or user.groups.filter(name="moderator").exists()

@receiver(m2m_changed, sender=User.groups.through)
def sync_attendance_on_user_groups_change(sender, instance, action, pk_set, **kwargs):
    """
    Sync attendance records when a user's group membership changes.

    Args:
        sender: The model class sending the signal.
        instance: The User instance whose groups changed.
        action: The type of change ('post_add', 'post_remove', etc.).
        pk_set: Set of Group primary keys added/removed.
        kwargs: Additional keyword arguments.
    """
    logger.debug(
        "m2m_changed signal received\n"
        f"Action: {action}\n"
        f"User: {instance}\n"
        f"Groups changed: {pk_set}\n"
        f"kwargs: {pprint.pformat(kwargs)}"
    )

    user = instance

    if action == 'post_add':
        # Find all schedules for the newly added groups
        schedules = Schedule.objects.filter(group__in=pk_set).distinct()
        attendance_to_create = []

        for schedule in schedules:
            if not user_is_staff_or_moderator(user):
                attendance_to_create.append(
                    Attendance(user=user, schedule=schedule, status='tbd')
                )

        if attendance_to_create:
            Attendance.objects.bulk_create(attendance_to_create, ignore_conflicts=True)
            logger.info(f"Created {len(attendance_to_create)} attendance records for user {user}.")

    elif action == 'post_remove':
        # Remove attendance records for schedules in the removed groups
        deleted_count, _ = Attendance.objects.filter(
            user=user, schedule__group__in=pk_set
        ).delete()
        logger.info(f"Deleted {deleted_count} attendance records for user {user}.")

@receiver(post_save, sender=Schedule)
def sync_attendance_on_schedule_group_change(sender, instance, created, **kwargs):
    """
    Sync attendance records when a Schedule's group changes or is created.

    Args:
        sender: The model class sending the signal.
        instance: The Schedule instance that was saved.
        created: Boolean, True if a new record was created.
        kwargs: Additional keyword arguments.
    """
    logger.debug(
        "post_save signal received\n"
        f"Schedule: {instance}\n"
        f"created: {created}\n"
        f"kwargs: {pprint.pformat(kwargs)}"
    )
    schedule = instance

    # Users who currently have attendance for this schedule
    users_with_attendance = User.objects.filter(
        attendances__schedule=schedule
    ).distinct()

    # Users in the current group of the schedule
    users_in_group = schedule.group.user_set.all() if schedule.group else User.objects.none()

    # Remove attendance for users no longer in the group
    users_to_remove = users_with_attendance.exclude(pk__in=users_in_group.values_list('pk', flat=True))
    if users_to_remove.exists():
        deleted_count, _ = Attendance.objects.filter(
            schedule=schedule, user__in=users_to_remove
        ).delete()
        logger.info(f"Deleted {deleted_count} attendance records for schedule {schedule}.")

    # Add attendance for new users in the group
    if schedule.group:
        users_to_add = users_in_group.exclude(pk__in=users_with_attendance.values_list('pk', flat=True))
        attendance_to_create = []

        for user in users_to_add:
            if not user_is_staff_or_moderator(user):
                attendance_to_create.append(
                    Attendance(user=user, schedule=schedule, status='tbd')
                )

        if attendance_to_create:
            Attendance.objects.bulk_create(attendance_to_create, ignore_conflicts=True)
            logger.info(f"Created {len(attendance_to_create)} attendance records for schedule {schedule}.")
