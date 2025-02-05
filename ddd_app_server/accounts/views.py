import requests

from urllib.parse import urljoin

from django.urls import reverse
from django.conf import settings
from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client

class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    callback_url = settings.GOOGLE_OAUTH_CALLBACK_URL
    client_class = OAuth2Client

class GoogleLoginCallback(APIView):
    def get(self, request, *args, **kwargs):
        code = request.GET.get('code')
        
        if code is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        token_endpoint_url = urljoin("http://localhost:8000", reverse("google_login"))
        response = requests.post(token_endpoint_url, data={"code": code})
        
        return Response(response.json(), status=status.HTTP_200_OK)

class GoogleLoginUrl(APIView):
    def get(self, request, *args, **kwargs):
        return Response({
            "url": "https://accounts.google.com/o/oauth2/v2/auth?redirect_uri={google_callback_uri}&prompt=consent&response_type=code&client_id={google_client_id}&scope=openid%20email%20profile&access_type=offline".format(
                google_callback_uri=settings.GOOGLE_OAUTH_CALLBACK_URL,
                google_client_id=settings.GOOGLE_OAUTH_CLIENT_ID
            )
        }, status=status.HTTP_200_OK)