import logging
from django.urls import reverse_lazy
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.apple.views import AppleOAuth2Adapter
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from common.mixins import BaseResponseMixin
from .serializers import (
    EmailTokenObtainSerializer,
    EmailCheckRequestSerializer,
    EmailCheckResponseSerializer
)


logger = logging.getLogger(__name__)


class CheckEmailUsedView(APIView, BaseResponseMixin):
    permission_classes = [AllowAny]  # No authentication required
    authentication_classes = []      # No authentication mechanisms applied

    @swagger_auto_schema(
        operation_summary="Check if Email is Used",
        operation_description=(
            "Accepts an email address in the POST request body and returns whether "
            "this email is already registered in the system. \n\n"
            "**Request Body:** `{'email': 'user@example.com'}`"
        ),
        request_body=EmailCheckRequestSerializer,  # Formal schema for the request body
        responses={
            status.HTTP_200_OK: openapi.Response(
                description="Email usage status successfully determined.",
                schema=EmailCheckResponseSerializer,  # Formal schema for the 200 OK response
                examples={
                    "application/json (Email is used)": {"code":200, "message":"Email check completed successfully", "data":{"email_used": True}},
                    "application/json (Email is not used)": {"code":200, "message":"Email check completed successfully.", "data":{"email_used": False}}
                }
            )
        }
    )
    def post(self, request, *args, **kwargs):
        request_serializer = EmailCheckRequestSerializer(data=request.data)

        if request_serializer.is_valid():
            email = request_serializer.validated_data['email']
            is_used = User.objects.filter(email__iexact=email).exists()

            response_data = {
                "code": 200,
                "message": "Email check completed successfully.",
                "data": {'email_used': is_used}
            }
            self.create_response(200, "Email check completed successfully.", response_data)
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response(request_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ObtainJWTFromSessionView(BaseResponseMixin, APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        refresh = RefreshToken.for_user(user)

        response_data = {
            'refresh_token': str(refresh),
            'access_token': str(refresh.access_token),
            'user': {
                'pk': user.pk,
                'username': user.username,
                'email': user.email,
            }
        }
        return self.create_response(200, 'JWT tokens generated successfully.', response_data)


class EmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = EmailTokenObtainSerializer


class ProfileView(LoginRequiredMixin, View):
    login_url = reverse_lazy('account_login')
    template_name = 'account/profile.html'

    def get(self, request, *args, **kwargs):
        user = request.user
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        logger.info(f"ProfileView: User {user.pk} ({user.get_username()}) accessed profile. JWTs generated.")

        context = {
            'user_object': user,
            'access_token': access_token,
            'refresh_token': refresh_token,
        }
        return render(request, self.template_name, context)


@method_decorator(csrf_exempt, name='dispatch')
class GoogleLoginView(SocialLoginView):
    authentication_classes = []
    permission_classes = []

    adapter_class = GoogleOAuth2Adapter


@method_decorator(csrf_exempt, name='dispatch')
class AppleLoginView(SocialLoginView):
    authentication_classes = []
    permission_classes = []

    adapter_class = AppleOAuth2Adapter
