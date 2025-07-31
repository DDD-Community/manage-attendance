from django.urls import path
from django.urls import include
from rest_framework_simplejwt.views import TokenBlacklistView
from dj_rest_auth.registration.views import RegisterView
from .views import (
    CheckEmailUsedView,
    ProfileView,
    # ObtainJWTFromSessionView,
    EmailTokenObtainPairView
)

urlpatterns = [
    # path("", include("dj_rest_auth.urls")),
    # path("registration/", include("dj_rest_auth.registration.urls")),
    path("registration/", RegisterView.as_view(), name="account_register"),
    path("token/blacklist/", TokenBlacklistView.as_view(), name="token_blacklist"),
    
    ## OAuth
    # path("oauth/", include("allauth.urls")),
    path('token/email/', EmailTokenObtainPairView.as_view(), name='token_obtain_email'),
    # path("token/session/", ObtainJWTFromSessionView.as_view(), name="session-to-jwt"),
    
    
    path("profile/", ProfileView.as_view(), name="account_profile"),
    
    
    path("check-email/", CheckEmailUsedView.as_view(), name="check_email_used"),
    # path("google/url/", GoogleLoginUrl.as_view(), name="google_login_url"),
    # path("google/login/", GoogleLoginView.as_view(), name="google_login"),
    # path("google/callback/", GoogleLoginCallback.as_view(), name="google_login_callback"),
    # path("apple/url/", AppleLoginUrl.as_view(), name="apple_login_url"),
    # path("apple/login/", AppleLoginView.as_view(), name="apple_login"),
    # path("apple/callback/", AppleLoginCallback.as_view(), name="apple_login_callback"),
]
