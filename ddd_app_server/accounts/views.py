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

logger = logging.getLogger(__name__)

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