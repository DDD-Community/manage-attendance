import logging
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.apple.views import AppleOAuth2Adapter
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from common.mixins import BaseResponseMixin
from django.urls import reverse_lazy
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import JsonResponse
from django.contrib.auth.models import User

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework import serializers

logger = logging.getLogger(__name__)

# --- Serializers for Formal Schema Definition ---

class EmailCheckRequestSerializer(serializers.Serializer):
    """
    Serializer for the email check request body.
    Defines the expected input structure and validation for the email.
    """
    email = serializers.EmailField(
        required=True,
        help_text="The email address you want to check for existence."
    )
    # To disallow any extra fields not defined in the serializer, you can add Meta class:
    # class Meta:
    #     extra = serializers.Extra.forbid

class EmailCheckResponseSerializer(serializers.Serializer):
    """
    Serializer for the successful email check response.
    Defines the output structure.
    """
    email_used = serializers.BooleanField(
        help_text="True if the email is already associated with an account, False otherwise."
    )

# --- API View using POST ---

class CheckEmailUsedView(APIView):
    """
    API endpoint to check if an email address is already in use.
    This endpoint uses the POST method and expects the email in the request body.
    """
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
                    "application/json (Email is used)": {"email_used": True},
                    "application/json (Email is not used)": {"email_used": False}
                }
            ),
            status.HTTP_400_BAD_REQUEST: openapi.Response(
                description=(
                    "Bad Request: The request body is invalid. This can occur if the 'email' field is missing, "
                    "not a valid email format, or if other validation rules defined in the "
                    "EmailCheckRequestSerializer are not met. The response will detail the errors."
                ),
                # drf-yasg will automatically infer the schema for validation errors
                # from the EmailCheckRequestSerializer.
                # It typically looks like: {"field_name": ["Error message."]}
                examples={
                    "application/json (Email field required)": {
                        "email": ["This field is required."]
                    },
                    "application/json (Invalid email format)": {
                        "email": ["Enter a valid email address."]
                    }
                }
            )
        }
    )
    def post(self, request, *args, **kwargs):
        """
        Handles POST requests to check email existence.
        """
        request_serializer = EmailCheckRequestSerializer(data=request.data)

        if request_serializer.is_valid():
            email = request_serializer.validated_data['email']
            # Perform a case-insensitive check for the email
            is_used = User.objects.filter(email__iexact=email).exists()

            response_data = {'email_used': is_used}
            # You can directly return response_data as it matches EmailCheckResponseSerializer's structure.
            # For consistency or if the response serializer had more complex logic/fields,
            # you could explicitly serialize the response:
            # response_payload_serializer = EmailCheckResponseSerializer(data=response_data)
            # response_payload_serializer.is_valid(raise_exception=True) # This should always be valid
            # return Response(response_payload_serializer.data, status=status.HTTP_200_OK)
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            # If validation fails, DRF's serializer.errors provides a structured error response
            return Response(request_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(LoginRequiredMixin, View):
    # LoginRequiredMixin이 인증되지 않은 사용자를 리디렉션할 URL
    # allauth의 기본 로그인 URL 이름은 'account_login' 입니다.
    # 만약 accounts.urls가 /api/accounts/ 에 마운트 되었다면,
    # 실제 URL은 /api/accounts/login/ 이 됩니다.
    login_url = reverse_lazy('account_login') # settings.LOGIN_URL 을 따르거나 직접 지정
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