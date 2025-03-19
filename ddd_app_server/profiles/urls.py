from django.urls import path
from .views import ProfileDetailView

# prefix = "profiles/"
urlpatterns = [
    path("", ProfileDetailView.as_view(), name='profile-detail'),
    path("<uuid:user_id>/", ProfileDetailView.as_view(), name='profile-detail-with-id'),
]
