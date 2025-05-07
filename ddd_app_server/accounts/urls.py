from django.urls import path
from django.urls import include
from django.urls import re_path
from .views import CheckEmailUsedView, ObtainJWTFromSessionView, ProfileView

urlpatterns = [
    path("", include("dj_rest_auth.urls")),
    path("registration/", include("dj_rest_auth.registration.urls")),
    
    ## OAuth
    path("", include("allauth.urls")),
    path("session-to-jwt/", ObtainJWTFromSessionView.as_view(), name="session-to-jwt"),
    
    
    # 프로필 페이지 URL (allauth의 기본 프로필 이름과 일치시킬 수 있음)
    path("profile/", ProfileView.as_view(), name="account_profile"),
    
    
    path("check-email/", CheckEmailUsedView.as_view(), name="check_email_used"),
    # path("google/url/", GoogleLoginUrl.as_view(), name="google_login_url"),
    # path("google/login/", GoogleLoginView.as_view(), name="google_login"),
    # path("google/callback/", GoogleLoginCallback.as_view(), name="google_login_callback"),
    # path("apple/url/", AppleLoginUrl.as_view(), name="apple_login_url"),
    # path("apple/login/", AppleLoginView.as_view(), name="apple_login"),
    # path("apple/callback/", AppleLoginCallback.as_view(), name="apple_login_callback"),
]