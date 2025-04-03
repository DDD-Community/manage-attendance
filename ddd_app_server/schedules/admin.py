from django.contrib import admin
from .models import Schedule, Attendance

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_time', 'end_time', 'created_at')
    search_fields = ('title', 'description')
    list_filter = ('start_time', 'end_time')
    ordering = ('-start_time',)

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('user', 'schedule', 'status', 'updated_at', 'method')
    search_fields = ('user__username', 'schedule__title')
    list_filter = ('status', 'method', 'updated_at')
    ordering = ('-updated_at',)
