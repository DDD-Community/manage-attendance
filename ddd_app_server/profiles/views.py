from rest_framework.views import APIView
from rest_framework import permissions, status, serializers
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from .models import Profile
from .serializers import ProfileSerializer
from common.mixins import BaseResponseMixin
from common.serializers import ErrorResponseSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication

# 프로필 조회/수정 성공 응답용 Serializer (Swagger 문서화에 사용)
class ProfileSuccessResponseSerializer(serializers.Serializer):
    code = serializers.IntegerField(default=200)
    message = serializers.CharField(default="프로필 정보를 성공적으로 조회했습니다.")
    data = ProfileSerializer()

# 현재 사용자 프로필 조회 및 수정 APIView
class ProfileDetailView(BaseResponseMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_object(self):
        # 현재 로그인한 사용자의 프로필 반환 (user.profile을 사용)
        return self.request.user.profile

    @swagger_auto_schema(
        tags=["profiles"],
        operation_summary="내 프로필 조회",
        operation_description="현재 로그인한 사용자의 프로필 정보를 조회합니다.",
        responses={200: ProfileSerializer()}
    )
    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = ProfileSerializer(instance)
        return self.create_response(200, "프로필 정보를 성공적으로 조회했습니다.", serializer.data)

    @swagger_auto_schema(
        tags=["profiles"],
        operation_summary="내 프로필 수정",
        operation_description="현재 로그인한 사용자의 프로필 정보를 부분 업데이트합니다.",
        request_body=ProfileSerializer,
        responses={
            200: ProfileSerializer(),
            400: ErrorResponseSerializer
        },
    )
    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        # serializer = ProfileSerializer(instance, data=request.data, partial=True)
        serializer = ProfileSerializer(instance, data=request.data, context={'request': request}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return self.create_response(200, "프로필이 성공적으로 수정되었습니다.", serializer.data)
        return self.create_response(400, "프로필 수정에 실패했습니다.", serializer.errors, status.HTTP_400_BAD_REQUEST)

# 특정 사용자 프로필 조회 APIView
class UserProfileDetailView(BaseResponseMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_object(self):
        profile_id = self.kwargs.get('profile_id')
        profile = get_object_or_404(Profile, id=profile_id)
        return profile

    @swagger_auto_schema(
        tags=["profiles"],
        operation_summary="사용자 프로필 조회",
        operation_description="지정된 사용자(profile_id)의 프로필 정보를 조회합니다.",
        responses={200: ProfileSerializer()}
    )
    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = ProfileSerializer(instance)
        return self.create_response(200, "사용자 프로필 정보를 성공적으로 조회했습니다.", serializer.data)
