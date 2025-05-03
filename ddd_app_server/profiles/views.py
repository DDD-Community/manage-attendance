from rest_framework.views import APIView
from rest_framework import permissions, status, serializers
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from .models import Profile
from .serializers import ProfileSerializer
from common.mixins import BaseResponseMixin
from common.serializers import ErrorResponseSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from .mixins import MyProfileMixin

# 특정 사용자 프로필 조회 APIView
class UserProfileDetailView(BaseResponseMixin, MyProfileMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @swagger_auto_schema(
        tags=["profiles"],
        operation_summary="프로필 조회",
        operation_description="프로필 정보를 조회합니다.",
        responses={200: ProfileSerializer()}
    )
    def get(self, request, *args, **kwargs):
        profile_id = self.kwargs.get('profile_id')
        profile = self.get_profile(profile_id)
        serializer = ProfileSerializer(profile)
        return self.create_response(200, "프로필 정보를 성공적으로 조회했습니다.", serializer.data)

    @swagger_auto_schema(
        tags=["profiles"],
        operation_summary="프로필 수정",
        operation_description="프로필 정보를 부분 업데이트합니다.",
        request_body=ProfileSerializer,
        responses={
            200: ProfileSerializer(),
            400: ErrorResponseSerializer
        },
    )
    def patch(self, request, *args, **kwargs):
        profile_id = self.kwargs.get('profile_id')
        profile = self.get_profile(profile_id)

        # Check if the user is the owner
        if not (request.user == profile.user):
            return self.create_response(403, "프로필을 수정할 권한이 없습니다.", {}, status.HTTP_403_FORBIDDEN)

        # Check if the user is a moderator
        if not (request.user.is_staff or request.user.groups.filter(name="moderator").exists()):
            return self.create_response(403, "프로필을 수정할 권한이 없습니다.", {}, status.HTTP_403_FORBIDDEN)

        serializer = ProfileSerializer(profile, data=request.data, context={'request': request}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return self.create_response(200, "프로필이 성공적으로 수정되었습니다.", serializer.data)
        return self.create_response(400, "프로필 수정에 실패했습니다.", serializer.errors, status.HTTP_400_BAD_REQUEST)

