from django.urls import path
from .views import QRCodeGenerateView, QRCodeValidateView

# # prefix = "schedules/"
# urlpatterns = [
#     path('', ScheduleListView.as_view(), name='schedule_list'),
#     path('<uuid:schedule_id>/', ScheduleDetailView.as_view(), name='schedule_detail'),
#     path('<uuid:schedule_id>/attendances/', AttendanceListView.as_view(), name='attendance_list'),
#     path('<uuid:schedule_id>/attendances/<uuid:user_id>/', AttendanceDetailView.as_view(), name='attendance_detail'),
# ]

# prefix = "qrcode/"
urlpatterns = [
    path('generate/', QRCodeGenerateView.as_view(), name="generate-qrcode"),
    path('validate/', QRCodeValidateView.as_view(), name="validate-qrcode"),
]
