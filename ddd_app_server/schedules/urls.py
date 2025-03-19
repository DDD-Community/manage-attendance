from django.urls import path
from .views import (
    ScheduleListView, 
    ScheduleDetailView, 
    ScheduleCreateView,
    ScheduleUpdateView,
    ScheduleDeleteView,
    AttendanceListView, 
    AttendanceDetailView,
    AttendanceUpdateView
)

# prefix = "schedules/"
urlpatterns = [
    # Schedule endpoints
    path('', ScheduleListView.as_view(), name='schedule_list'),
    path('create/', ScheduleCreateView.as_view(), name='schedule_create'),
    path('<uuid:schedule_id>/', ScheduleDetailView.as_view(), name='schedule_detail'),
    path('<uuid:schedule_id>/update/', ScheduleUpdateView.as_view(), name='schedule_update'),
    path('<uuid:schedule_id>/delete/', ScheduleDeleteView.as_view(), name='schedule_delete'),
    
    # Attendance endpoints
    path('<uuid:schedule_id>/attendances/', AttendanceListView.as_view(), name='attendance_list'),
    path('<uuid:schedule_id>/attendances/<uuid:user_id>/', AttendanceDetailView.as_view(), name='attendance_detail'),
    path('<uuid:schedule_id>/attendances/update/', AttendanceUpdateView.as_view(), name='attendance_update'),
]
