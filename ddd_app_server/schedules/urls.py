from django.urls import path
from .views import (
    ScheduleListView, 
    ScheduleDetailView, 
    AttendanceListView, 
    AttendanceDetailView
)

# prefix = "schedules/"
urlpatterns = [
    path('', ScheduleListView.as_view(), name='schedule_list'),
    path('<uuid:schedule_id>/', ScheduleDetailView.as_view(), name='schedule_detail'),
    path('<uuid:schedule_id>/attendances/', AttendanceListView.as_view(), name='attendance_list'),
    path('<uuid:schedule_id>/attendances/<uuid:user_id>/', AttendanceDetailView.as_view(), name='attendance_detail'),
]
