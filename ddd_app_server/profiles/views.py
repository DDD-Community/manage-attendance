from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from .models import Profile
from .serializers import ProfileSerializer

class BaseResponseMixin:
    def create_response(self, code, message, data=None, status_code=status.HTTP_200_OK):
        return Response({
            "code": code,
            "message": message,
            "data": data
        }, status=status_code)

class IsAdminOrModerator(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_staff or request.user.groups.filter(name="moderator").exists()
        )

# 프로필 조회 및 수정 뷰
class ProfileDetailView(generics.RetrieveUpdateAPIView, BaseResponseMixin):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user.profile

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return self.create_response(200, "프로필 정보를 성공적으로 조회했습니다.", serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            self.perform_update(serializer)
            return self.create_response(200, "프로필이 성공적으로 수정되었습니다.", serializer.data)
        return self.create_response(400, "프로필 수정에 실패했습니다.", serializer.errors, status.HTTP_400_BAD_REQUEST)

class UserProfileDetailView(generics.RetrieveAPIView, BaseResponseMixin):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        user_id = self.kwargs.get('user_id')
        return get_object_or_404(Profile, user_id=user_id)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return self.create_response(200, "사용자 프로필 정보를 성공적으로 조회했습니다.", serializer.data)