from django.urls import path
from .views import InviteCodeCreateView, InviteCodeValidateView

# prefix = "invite-code/"
urlpatterns = [
    path("", InviteCodeCreateView.as_view(), name="invite-code-create"),  # Create an invite code
    path("validate/", InviteCodeValidateView.as_view(), name="invite-code-validate"),  # Validate an invite code
]
