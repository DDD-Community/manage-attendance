# schedules/models.py
import uuid
from django.db import models
from django.contrib.auth.models import Group #, User
from profiles.models import Cohort


class Schedule(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, help_text="Unique identifier for the schedule.")
    title = models.CharField(max_length=200, help_text="The title of the schedule.")
    description = models.TextField(blank=True, help_text="A detailed description of the schedule.")
    start_time = models.DateTimeField(help_text="The date and time when the schedule starts.")
    end_time = models.DateTimeField(help_text="The date and time when the schedule ends.")
    created_at = models.DateTimeField(auto_now_add=True, editable=False, help_text="Timestamp when the schedule was created.")
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, related_name='schedules', help_text="The group to which this schedule is assigned.")
    cohort = models.ForeignKey(Cohort, on_delete=models.SET_NULL, null=True, blank=True, related_name='schedules')

    class Meta:
        ordering = ['start_time', 'title']

    def __str__(self):
        return f"{self.title} ({self.start_time.strftime('%Y-%m-%d %H:%M')})"

    # # Example property to easily get assigned users via the group
    # @property
    # def assigned_users_through_group(self):
    #     """Returns a queryset of users belonging to the assigned group."""
    #     if self.assigned_group:
    #         return self.assigned_group.user_set.all()
    #     return User.objects.none() # Return an empty queryset if no group is assigned

# from django.contrib.auth.models import User
