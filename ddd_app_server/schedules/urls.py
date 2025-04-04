# from django.urls import path
# from .views import (
#     ScheduleListView, 
#     ScheduleDetailView, 
#     AttendanceListView, 
#     AttendanceDetailView
# )

# # prefix = "schedules/"
# urlpatterns = [
#     # Schedule endpoints
#     path('', ScheduleListView.as_view(), name='schedule-list'),
#     path('<uuid:schedule_id>/', ScheduleDetailView.as_view(), name='schedule-detail'),
#     # Attendance endpoints
#     path('<uuid:schedule_id>/attendances/', AttendanceListView.as_view(), name='attendance-list'),
#     path('<uuid:schedule_id>/attendances/<int:user_id>/', AttendanceDetailView.as_view(), name='attendance-detail'),
# ]

from django.urls import path, re_path
from .views import (
    ScheduleListView, 
    ScheduleDetailView, 
    AttendanceListView, 
    AttendanceDetailView,
)

urlpatterns = [
    # Schedule endpoints
    path('', ScheduleListView.as_view(), name='schedule-list'),
    re_path(r'^(?P<schedule_id>(now|[0-9a-f-]{36}))/$', ScheduleDetailView.as_view(), name='schedule-detail'),
    # Attendance endpoints
    re_path(r'^(?P<schedule_id>(now|[0-9a-f-]{36}))/attendances/$', AttendanceListView.as_view(), name='attendance-list'),
    re_path(r'^(?P<schedule_id>(now|[0-9a-f-]{36}))/attendances/(?P<user_id>\d+)/$', AttendanceDetailView.as_view(), name='attendance-detail'),
]
