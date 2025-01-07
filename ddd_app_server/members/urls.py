from django.urls import path
from . import views

# # prefix = "invite-code/"
# urlpatterns = [
#     path("", views.InviteCodeCreateView.as_view(), name="invite-code-create"),  # Create an invite code
#     path("validation/", views.InviteCodeValidationView.as_view(), name="invite-code-validation"),  # Validate an invite code
# ]

# prefix = "members/"
urlpatterns = [
    # path("", views.MemberListView.as_view(), name="member-list"),  # List all members
    # path("<uuid:member_id>/", views.MemberDetailView.as_view(), name="member-detail"),  # Detail of a specific member
    # path("<uuid:member_id>/attendance/", views.MemberAttendanceView.as_view(), name="member-attendance"),  # Attendance of a specific member
]
