from django.contrib import admin
from django.urls import include, path
from accounts.views import GoogleLogin
from ddd_app_server.health import health_check
# from rest_framework.routers import DefaultRouter

# # Assuming you are using DRF viewsets
# router = DefaultRouter()

# URL patterns
urlpatterns = [
    path("admin/", admin.site.urls),
    # path("", include(router.urls)),  # Default router, if using viewsets
    # path("api-auth/", include('rest_framework.urls', namespace='rest_framework')),
    path('health/', health_check),

    path("accounts/", include('allauth.urls')),
    path("accounts/", include('accounts.urls')),  # Include account-related URLs
    
    path("dj-rest-auth/", include('dj_rest_auth.urls')),  # Include DJ Rest Auth URLs
    path("dj-rest-auth/registration/", include('dj_rest_auth.registration.urls')),  # Include DJ Rest Auth registration URLs
    path("dj-rest-auth/google/", GoogleLogin.as_view(), name='google_login'),
    
    path("invite-code/", include('invite.urls')),  # Include invite code URLs
    path("members/", include('members.urls')),  # Include member-related URLs
    path("schedules/", include('schedules.urls')),  # Include schedule-related URLs
]
