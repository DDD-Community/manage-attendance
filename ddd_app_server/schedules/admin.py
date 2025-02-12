from django.contrib import admin
from .models import Schedule

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'start_time', 'end_time', 'created_at')
    list_filter = ('start_time', 'end_time')
    search_fields = ('title', 'description')
    ordering = ('start_time',)

