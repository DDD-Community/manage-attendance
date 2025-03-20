from django.utils.timezone import now
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import Group
from .models import Schedule, Attendance
from .serializers import ScheduleSerializer, AttendanceSerializer

# Custom Permission for Admins and Moderators
class IsAdminOrModerator(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_staff or request.user.groups.filter(name="moderator").exists()
        )

class BaseResponseMixin:
    def create_response(self, code, message, data=None, status_code=status.HTTP_200_OK):
        return Response({
            "code": code,
            "message": message,
            "data": data
        }, status=status_code)

class ScheduleListView(generics.ListCreateAPIView, BaseResponseMixin):
    serializer_class = ScheduleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.method == 'GET':
            return Schedule.objects.filter(attendances__user=self.request.user).distinct()
        return Schedule.objects.all()

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminOrModerator()]
        return [permissions.IsAuthenticated()]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return self.create_response(200, "스케줄 목록을 성공적으로 조회했습니다.", serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return self.create_response(201, "스케줄이 성공적으로 생성되었습니다.", serializer.data)
        return self.create_response(400, "스케줄 생성에 실패했습니다.", serializer.errors, status.HTTP_400_BAD_REQUEST)

class ScheduleDetailView(generics.RetrieveUpdateDestroyAPIView, BaseResponseMixin):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAdminOrModerator()]
        return [permissions.IsAuthenticated()]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return self.create_response(200, "스케줄 상세 정보를 성공적으로 조회했습니다.", serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            self.perform_update(serializer)
            return self.create_response(200, "스케줄이 성공적으로 수정되었습니다.", serializer.data)
        return self.create_response(400, "스케줄 수정에 실패했습니다.", serializer.errors, status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return self.create_response(200, "스케줄이 성공적으로 삭제되었습니다.")

class AttendanceListView(generics.ListAPIView, BaseResponseMixin):
    serializer_class = AttendanceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        schedule_id = self.kwargs.get('schedule_id')
        if self.request.user.is_staff or self.request.user.groups.filter(name="moderator").exists():
            return Attendance.objects.filter(schedule_id=schedule_id)
        return Attendance.objects.filter(schedule_id=schedule_id, user=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return self.create_response(200, "출석 목록을 성공적으로 조회했습니다.", serializer.data)

class AttendanceDetailView(generics.RetrieveUpdateAPIView, BaseResponseMixin):
    serializer_class = AttendanceSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'user_id'
    lookup_url_kwarg = 'user_id'

    def get_queryset(self):
        schedule_id = self.kwargs.get('schedule_id')
        if self.request.user.is_staff or self.request.user.groups.filter(name="moderator").exists():
            return Attendance.objects.filter(schedule_id=schedule_id)
        return Attendance.objects.filter(schedule_id=schedule_id, user=self.request.user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user_id'] = self.kwargs.get('user_id')
        return context

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return self.create_response(200, "출석 상세 정보를 성공적으로 조회했습니다.", serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        schedule = instance.schedule

        if not (schedule.start_time <= now() <= schedule.end_time):
            return self.create_response(400, "현재 출석을 등록할 수 없는 시간입니다.", None, status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            self.perform_update(serializer)
            return self.create_response(200, "출석이 성공적으로 업데이트되었습니다.", serializer.data)
        return self.create_response(400, "출석 업데이트에 실패했습니다.", serializer.errors, status.HTTP_400_BAD_REQUEST)
