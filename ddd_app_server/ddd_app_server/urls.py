from django.contrib import admin
from django.urls import include, path
# from rest_framework.routers import DefaultRouter

# # Assuming you are using DRF viewsets
# router = DefaultRouter()

# URL patterns
urlpatterns = [
    path("admin/", admin.site.urls),
    # path("", include(router.urls)),  # Default router, if using viewsets
    # path("api-auth/", include('rest_framework.urls', namespace='rest_framework')),
    path("accounts/", include('allauth.urls')),
    path("invite-code/", include('invite.urls')),  # Include invite code URLs
    path("members/", include('members.urls')),  # Include member-related URLs
    path("schedules/", include('schedules.urls')),  # Include schedule-related URLs
]
