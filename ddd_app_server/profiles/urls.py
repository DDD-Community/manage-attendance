from django.urls import path
from .views import ProfileDetailView, UserProfileDetailView

# prefix = "profiles/"
urlpatterns = [
    # Profile endpoints
    path('me/', ProfileDetailView.as_view(), name='profile-detail'),
    path('<int:user_id>/', UserProfileDetailView.as_view(), name='user-profile-detail'),
]
