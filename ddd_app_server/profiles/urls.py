from django.urls import path, re_path
from .views import ProfileDetailView

# prefix = "profiles/"
urlpatterns = [
    # Profile endpoints
    path('me/', ProfileDetailView.as_view(), name='profile-detail-me'),
    path('<uuid:profile_id>/', ProfileDetailView.as_view(), name='profile-detail'),
    # re_path(r'^(?P<profile_id>(me|[0-9a-f-]{36}))/$', ProfileDetailView.as_view(), name='profile-detail'),
]
