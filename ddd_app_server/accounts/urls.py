from django.urls import path
from django.urls import include
from django.urls import re_path
from .views import GoogleLogin, GoogleLoginCallback, GoogleLoginUrl

urlpatterns = [
    path("", include("dj_rest_auth.urls")),
    re_path(r"^accounts/", include("allauth.urls")),
    # /login, /logout,
    # /password/reset, /password/reset/confirm, /password/change,
    # /user
    # /token/verify, /token/refresh
    path("google/url/", GoogleLoginUrl.as_view(), name="google_login_url"),
    path("google/login/", GoogleLogin.as_view(), name="google_login"),
    path("google/callback/", GoogleLoginCallback.as_view(), name="google_login_callback"),
]