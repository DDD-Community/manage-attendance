# admin.py
from django.contrib import admin
from django.contrib.auth import get_user_model
from attendances.models import Attendance

User = get_user_model()

# --- Attendance Admin (No changes needed based on request) ---
@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('user', 'schedule', 'status', 'updated_at', 'method')
    search_fields = ('user__username', 'schedule__title')
    list_filter = ('status', 'method', 'updated_at', 'user', 'schedule') # Filter by schedule's group
    ordering = ('-updated_at',)
