from django.urls import path
from .views import ProfileDetailView, UserProfileDetailView

# prefix = "profiles/"
urlpatterns = [
    # Profile endpoints
    path('<uuid:profile_id>/', UserProfileDetailView.as_view(), name='profile-detail'),
]
