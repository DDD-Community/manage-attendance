from django.urls import path
from . import views

# prefix = "invite-code/"
urlpatterns = [
    path("", views.InviteCodeCreateView.as_view(), name="invite-code-create"),  # Create an invite code
    path("validate/", views.InviteCodeValidateView.as_view(), name="invite-code-validate"),  # Validate an invite code
]
