from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from .models import Schedule, Attendance

User = get_user_model()

@admin.action(description="Assign 'member' group to selected schedules")
def assign_member_group(modeladmin, request, queryset):
    # Ensure the 'member' group exists
    group, created = Group.objects.get_or_create(name='member')
    if created:
        modeladmin.message_user(request, "Created group 'member'.")

    # Assign the group to the selected schedules
    for schedule in queryset:
        schedule.assigned_groups.add(group)  # Assuming Schedule has a ManyToManyField to Group
        schedule.save()
        for user in group.user_set.all():
            Attendance.objects.get_or_create(
                user=user,
                schedule=schedule,
                defaults={'status': 'tbd'}
            )

    modeladmin.message_user(request, f"Assigned 'member' group to {queryset.count()} schedules.")

@admin.action(description="Assign users in 'member' group to selected schedules")
def assign_member_users(modeladmin, request, queryset):
    # Get the 'member' group
    try:
        group = Group.objects.get(name='member')
    except Group.DoesNotExist:
        modeladmin.message_user(request, "Group 'member' does not exist.", level='error')
        return

    # Get all users in the 'member' group
    member_users = group.user_set.all()

    # Assign these users to the selected schedules
    for schedule in queryset:
        schedule.assigned_users.add(*member_users)  # Assuming Schedule has a ManyToManyField to User
        schedule.save()
        for user in member_users:
            Attendance.objects.get_or_create(
                user=user,
                schedule=schedule,
                defaults={'status': 'tbd'}
            )

    modeladmin.message_user(
        request,
        f"Assigned {member_users.count()} users from 'member' group to {queryset.count()} schedules."
    )

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_time', 'end_time', 'created_at')
    search_fields = ('title', 'description')
    list_filter = ('start_time', 'end_time')
    ordering = ('-start_time',)
    
    filter_horizontal = ('assigned_users', 'assigned_groups')
    actions = [assign_member_group, assign_member_users]

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('user', 'schedule', 'status', 'updated_at', 'method')
    search_fields = ('user__username', 'schedule__title')
    list_filter = ('status', 'method', 'updated_at')
    ordering = ('-updated_at',)
