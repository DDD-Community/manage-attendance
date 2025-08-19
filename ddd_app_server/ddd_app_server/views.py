from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.apple.views import AppleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken 
import logging

logger = logging.getLogger(__name__)

class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    client_class = OAuth2Client

    def post(self, request, *args, **kwargs):
        # request.data에 id_token이 담겨 올 것을 예상
        # dj-rest-auth의 SocialLoginView는 내부적으로 access_token 필드를 사용하므로,
        # id_token을 access_token으로 매핑해줍니다.
        if 'id_token' in request.data:
            request.data['access_token'] = request.data['id_token']
        
        return super().post(request, *args, **kwargs)


class AppleLogin(SocialLoginView):
    adapter_class = AppleOAuth2Adapter
    client_class = OAuth2Client

    def post(self, request, *args, **kwargs):
        # Apple 로그인은 id_token을 access_token으로 사용합니다.
        if 'id_token' in request.data:
            request.data['access_token'] = request.data['id_token']
        
        return super().post(request, *args, **kwargs)


class DeactivateUserView(APIView):
    """
    요청을 보낸 사용자의 계정을 비활성화합니다.
    (is_active=False)
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        
        # 사용자를 비활성화 상태로 변경
        user.is_active = False
        user.save()

        try:
            # request body에 refresh 토큰이 포함되어 있다고 가정
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception as e:
            logger.error(f"토큰 무효화 실패: {e}")
            pass

        return Response({"detail": "계정이 성공적으로 비활성화되었습니다."}, status=status.HTTP_200_OK)