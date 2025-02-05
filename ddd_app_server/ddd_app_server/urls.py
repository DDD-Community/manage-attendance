from django.contrib import admin
from django.urls import include, path
from ddd_app_server.health import health_check
# from rest_framework.routers import DefaultRouter

# # Assuming you are using DRF viewsets
# router = DefaultRouter()

# URL patterns
urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", health_check),
    path("auth/", include('accounts.urls')),  # Include account-related URLs
    
    path("invite-code/", include('invite.urls')),  # Include invite code URLs
    path("members/", include('members.urls')),  # Include member-related URLs
    path("schedules/", include('schedules.urls')),  # Include schedule-related URLs
]
