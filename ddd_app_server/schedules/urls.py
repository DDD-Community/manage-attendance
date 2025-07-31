from django.urls import path
from .views import (
    ScheduleListView, 
    ScheduleDetailView,
)

urlpatterns = [
    # Schedule endpoints
    path('', ScheduleListView.as_view(), name='schedule-list'),
    path('<uuid:schedule_id>/', ScheduleDetailView.as_view(), name='schedule-detail'),
]
