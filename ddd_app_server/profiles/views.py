import logging
from django.http import Http404
from rest_framework import permissions, status, serializers
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_yasg.utils import swagger_auto_schema
from common.mixins import BaseResponseMixin
from common.serializers import ErrorResponseSerializer
from .mixins import CurrentProfileMixin
from .serializers import ProfileSerializer

logger = logging.getLogger(__name__)

# 프로필 조회 성공 응답 Serializer
class ProfileSuccesSerializer(serializers.Serializer):
    code = serializers.IntegerField(default=200)
    message = serializers.CharField(default="프로필 조회에 성공했습니다.")
    data = ProfileSerializer()

# 특정 사용자 프로필 조회 APIView
class ProfileDetailView(BaseResponseMixin, CurrentProfileMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @swagger_auto_schema(
        tags=["profiles"],
        operation_summary="프로필 조회",
        operation_description="프로필 정보를 조회합니다.",
        responses={
            200: ProfileSuccesSerializer,
            400: ErrorResponseSerializer
        },
    )
    def get(self, request, *args, **kwargs):
        profile_id = self.kwargs.get('profile_id', 'me')
        try:
            profile = self.get_profile(profile_id)
            serializer = ProfileSerializer(profile)
            return self.create_response(200, "프로필 정보를 성공적으로 조회했습니다.", serializer.data)
        except Http404:
            return self.create_response(404, "프로필을 찾을 수 없습니다.", None, status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        tags=["profiles"],
        operation_summary="프로필 수정",
        operation_description="프로필 정보를 부분 업데이트합니다.",
        request_body=ProfileSerializer,
        responses={
            200: ProfileSuccesSerializer,
            400: ErrorResponseSerializer
        },
    )
    def patch(self, request, *args, **kwargs):
        profile_id = self.kwargs.get('profile_id')
        profile = self.get_profile(profile_id)


        # Permission Check: Is the requester the owner or staff?
        is_owner = (profile.user == request.user)
        is_staff = (request.user.is_staff or request.user.groups.filter(name="moderator").exists())

        # Check if the user is the owner or a moderator
        if not (is_owner or is_staff):
            return self.create_response(403, "프로필을 수정할 권한이 없습니다.", {}, status.HTTP_403_FORBIDDEN)

        serializer = ProfileSerializer(profile, data=request.data, context={'request': request}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return self.create_response(200, "프로필이 성공적으로 수정되었습니다.", serializer.data)
        else:
            logger.error(f"Serializer errors: {serializer.errors}")
            return self.create_response(400, "프로필 수정에 실패했습니다.", serializer.errors, status.HTTP_400_BAD_REQUEST)

