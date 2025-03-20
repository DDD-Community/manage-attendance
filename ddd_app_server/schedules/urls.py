from django.urls import path
from .views import (
    ScheduleListView, 
    ScheduleDetailView, 
    AttendanceListView, 
    AttendanceDetailView
)

# prefix = "schedules/"
urlpatterns = [
    # Schedule endpoints
    path('', ScheduleListView.as_view(), name='schedule-list'),
    path('<uuid:schedule_id>/', ScheduleDetailView.as_view(), name='schedule-detail'),
    # Attendance endpoints
    path('<uuid:schedule_id>/attendances/', AttendanceListView.as_view(), name='attendance-list'),
    path('<uuid:schedule_id>/attendances/<int:user_id>/', AttendanceDetailView.as_view(), name='attendance-detail'),
]
