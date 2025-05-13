from django.urls import path
from .views import (
    AttendanceListView,
    AttendanceDetailView,
    AttendanceCountView
)

urlpatterns = [
    # Attendance endpoints
    path('', AttendanceListView.as_view(), name='attendance-list'),
    path('count/', AttendanceCountView.as_view(), name='attendance-count'),
    path('<uuid:attendance_id>/', AttendanceDetailView.as_view(), name='attendance-detail'),
]
