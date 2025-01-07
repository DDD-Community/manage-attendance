from django.urls import path
from . import views

# prefix = "invite-code/"
urlpatterns = [
    path("", views.InviteCodeCreateView.as_view(), name="invite-code-create"),  # Create an invite code
    path("validation/", views.InviteCodeValidationView.as_view(), name="invite-code-validation"),  # Validate an invite code
]
