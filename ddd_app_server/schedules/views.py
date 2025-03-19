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

# 스케줄 목록 조회 (사용자 본인의 스케줄만 조회 가능)
class ScheduleListView(generics.ListAPIView, BaseResponseMixin):
    serializer_class = ScheduleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Schedule.objects.filter(attendances__user=self.request.user).distinct()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return self.create_response(200, "스케줄 목록을 성공적으로 조회했습니다.", serializer.data)

# 스케줄 생성 (관리자 및 운영진만 가능)
class ScheduleCreateView(generics.CreateAPIView, BaseResponseMixin):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer
    permission_classes = [IsAdminOrModerator]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return self.create_response(201, "스케줄이 성공적으로 생성되었습니다.", serializer.data)
        return self.create_response(400, "스케줄 생성에 실패했습니다.", serializer.errors, status.HTTP_400_BAD_REQUEST)

# 스케줄 상세 조회
class ScheduleDetailView(generics.RetrieveAPIView, BaseResponseMixin):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return self.create_response(200, "스케줄 상세 정보를 성공적으로 조회했습니다.", serializer.data)

# 스케줄 수정 (관리자 및 운영진만 가능)
class ScheduleUpdateView(generics.UpdateAPIView, BaseResponseMixin):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer
    permission_classes = [IsAdminOrModerator]

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            self.perform_update(serializer)
            return self.create_response(200, "스케줄이 성공적으로 수정되었습니다.", serializer.data)
        return self.create_response(400, "스케줄 수정에 실패했습니다.", serializer.errors, status.HTTP_400_BAD_REQUEST)

# 스케줄 삭제 (관리자 및 운영진만 가능)
class ScheduleDeleteView(generics.DestroyAPIView, BaseResponseMixin):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer
    permission_classes = [IsAdminOrModerator]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return self.create_response(200, "스케줄이 성공적으로 삭제되었습니다.")

class AttendanceListView(generics.ListAPIView, BaseResponseMixin):
    serializer_class = AttendanceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        schedule_id = self.kwargs.get('schedule_id')
        return Attendance.objects.filter(schedule_id=schedule_id)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return self.create_response(200, "출석 목록을 성공적으로 조회했습니다.", serializer.data)

class AttendanceDetailView(generics.RetrieveAPIView, BaseResponseMixin):
    serializer_class = AttendanceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        schedule_id = self.kwargs.get('schedule_id')
        user_id = self.kwargs.get('user_id')
        return Attendance.objects.filter(schedule_id=schedule_id, user_id=user_id)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return self.create_response(200, "출석 상세 정보를 성공적으로 조회했습니다.", serializer.data)

# 출석 등록 및 수정 (사용자는 자신의 출석만 수정 가능)
class AttendanceUpdateView(APIView, BaseResponseMixin):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, schedule_id, *args, **kwargs):
        schedule = get_object_or_404(Schedule, id=schedule_id)
        user = request.user

        # 출석 가능 여부 체크 (현재 시간이 스케줄 진행 시간 내에 있는지 확인)
        if not (schedule.start_time <= now() <= schedule.end_time):
            return self.create_response(400, "현재 출석을 등록할 수 없는 시간입니다.", None, status.HTTP_400_BAD_REQUEST)

        # 사용자 출석 정보 가져오기 (없으면 새로 생성)
        attendance, created = Attendance.objects.get_or_create(user=user, schedule=schedule)
        
        # 출석 상태 업데이트
        attendance.status = request.data.get("status", attendance.status)
        attendance.method = request.data.get("method", attendance.method)
        attendance.attendance_time = now()
        attendance.note = request.data.get("note", attendance.note)
        attendance.save()

        serializer = AttendanceSerializer(attendance)
        return self.create_response(200, "출석이 성공적으로 업데이트되었습니다.", serializer.data)
