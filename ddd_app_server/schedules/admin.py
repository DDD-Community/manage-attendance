# admin.py
from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import Schedule
from attendances.models import Attendance

User = get_user_model()

# --- New Admin Action ---
@admin.action(description="Sync attendance for assigned group on selected schedules")
def sync_attendance_for_group(modeladmin, request, queryset):
    """
    Admin action to create/ensure attendance records for all users
    in the assigned group of the selected schedules.
    """
    schedules_processed = 0
    attendance_created_count = 0
    schedules_without_group = 0

    for schedule in queryset:
        if schedule.group:
            group = schedule.group
            users_in_group = group.user_set.all()
            
            if not users_in_group.exists():
                # Optional: message if the group has no users
                # modeladmin.message_user(request, f"Schedule '{schedule.title}' assigned group '{group.name}' has no users.", level='warning')
                continue # Skip to next schedule if group is empty

            created_for_this_schedule = 0
            for user in users_in_group:
                # Use get_or_create to add attendance only if it doesn't exist
                attendance, created = Attendance.objects.get_or_create(
                    user=user,
                    schedule=schedule,
                    defaults={'status': 'tbd'} # Set default status only if created
                )
                if created:
                    created_for_this_schedule += 1
            
            if created_for_this_schedule > 0:
                 attendance_created_count += created_for_this_schedule
            schedules_processed += 1
        else:
            schedules_without_group += 1
            modeladmin.message_user(request, f"Schedule '{schedule.title}' has no assigned group.", level='warning')

    # --- User Feedback ---
    message_parts = []
    if schedules_processed > 0:
        message_parts.append(f"Processed {schedules_processed} schedule(s) with assigned groups.")
    if attendance_created_count > 0:
        message_parts.append(f"Created {attendance_created_count} new attendance record(s).")
    if schedules_without_group > 0:
         message_parts.append(f"Skipped {schedules_without_group} schedule(s) with no assigned group.")
    
    if not message_parts:
         message = "No schedules selected or no action taken."
    else:
         message = " ".join(message_parts)

    modeladmin.message_user(request, message)


# --- Updated Schedule Admin ---
@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('title', 'group', 'start_time', 'end_time', 'created_at') # Added group
    search_fields = ('title', 'description', 'group__name') # Search by group name
    list_filter = ('start_time', 'end_time', 'group') # Filter by group
    ordering = ('-start_time',)
    
    # filter_horizontal is removed as ManyToManyFields are gone
    # Use raw_id_fields or autocomplete_fields for ForeignKey if needed, especially with many groups
    raw_id_fields = ('group',)

    actions = [sync_attendance_for_group]

