from django.utils.timezone import now
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from .models import Schedule, Attendance
from .serializers import ScheduleSerializer, AttendanceSerializer
from common.mixins import BaseResponseMixin
from common.serializers import ErrorResponseSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication

# 관리자나 모더레이터 전용 권한 클래스
class IsAdminOrModerator(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_staff or request.user.groups.filter(name="moderator").exists()
        )

# ── Schedule 관련 Response Wrapper ──

# 스케줄 목록 조회 응답
class ScheduleListResponseSerializer(serializers.Serializer):
    code = serializers.IntegerField(default=200)
    message = serializers.CharField(default="스케줄 목록을 성공적으로 조회했습니다.")
    data = ScheduleSerializer(many=True)

# 스케줄 생성 응답
class ScheduleCreateResponseSerializer(serializers.Serializer):
    code = serializers.IntegerField(default=201)
    message = serializers.CharField(default="스케줄이 성공적으로 생성되었습니다.")
    data = ScheduleSerializer()

# 스케줄 상세 조회 응답
class ScheduleDetailResponseSerializer(serializers.Serializer):
    code = serializers.IntegerField(default=200)
    message = serializers.CharField(default="스케줄 상세 정보를 성공적으로 조회했습니다.")
    data = ScheduleSerializer()

# 스케줄 수정 응답
class ScheduleUpdateResponseSerializer(serializers.Serializer):
    code = serializers.IntegerField(default=200)
    message = serializers.CharField(default="스케줄이 성공적으로 수정되었습니다.")
    data = ScheduleSerializer()

# 스케줄 삭제 응답
class ScheduleDeleteResponseSerializer(serializers.Serializer):
    code = serializers.IntegerField(default=200)
    message = serializers.CharField(default="스케줄이 성공적으로 삭제되었습니다.")
    data = serializers.JSONField(allow_null=True)

# ── Attendance 관련 Response Wrapper ──

# 출석 목록 조회 응답
class AttendanceListResponseSerializer(serializers.Serializer):
    code = serializers.IntegerField(default=200)
    message = serializers.CharField(default="출석 목록을 성공적으로 조회했습니다.")
    data = AttendanceSerializer(many=True)

# 출석 상세 조회 응답
class AttendanceDetailResponseSerializer(serializers.Serializer):
    code = serializers.IntegerField(default=200)
    message = serializers.CharField(default="출석 상세 정보를 성공적으로 조회했습니다.")
    data = AttendanceSerializer()

# 출석 업데이트 응답
class AttendanceUpdateResponseSerializer(serializers.Serializer):
    code = serializers.IntegerField(default=200)
    message = serializers.CharField(default="출석이 성공적으로 업데이트되었습니다.")
    data = AttendanceSerializer()

# ── ScheduleListView: 스케줄 목록 조회 및 생성 ──
class ScheduleListView(BaseResponseMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    serializer_class = ScheduleSerializer

    @swagger_auto_schema(
        tags=["schedule"],
        operation_summary="스케줄 목록 조회",
        operation_description="현재 사용자가 참여한 스케줄 목록을 조회합니다.",
        responses={200: ScheduleListResponseSerializer()}
    )
    def get(self, request, *args, **kwargs):
        queryset = Schedule.objects.filter(attendances__user=request.user).distinct()
        serializer = self.serializer_class(queryset, many=True)
        return self.create_response(200, "스케줄 목록을 성공적으로 조회했습니다.", serializer.data)

    @swagger_auto_schema(
        tags=["schedule"],
        operation_summary="스케줄 생성",
        operation_description="새로운 스케줄을 생성합니다.",
        request_body=ScheduleSerializer,
        responses={
            201: ScheduleCreateResponseSerializer(),
            400: ErrorResponseSerializer()
        }
    )
    def post(self, request, *args, **kwargs):
        # Check for admin or moderator permission manually
        if not (request.user.is_staff or request.user.groups.filter(name="moderator").exists()):
            return self.create_response(403, "스케줄 생성 권한이 없습니다.", None, status.HTTP_403_FORBIDDEN)
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return self.create_response(201, "스케줄이 성공적으로 생성되었습니다.", serializer.data, status.HTTP_201_CREATED)
        return self.create_response(400, "스케줄 생성에 실패했습니다.", serializer.errors, status.HTTP_400_BAD_REQUEST)

# ── ScheduleDetailView: 스케줄 상세 조회, 수정, 삭제 ──
class ScheduleDetailView(BaseResponseMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    serializer_class = ScheduleSerializer

    def get_object(self):
        schedule_id = self.kwargs.get('schedule_id')
        return get_object_or_404(Schedule, id=schedule_id)

    @swagger_auto_schema(
        tags=["schedule"],
        operation_summary="스케줄 상세 조회",
        operation_description="특정 스케줄의 상세 정보를 조회합니다.",
        responses={200: ScheduleDetailResponseSerializer()}
    )
    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.serializer_class(instance)
        return self.create_response(200, "스케줄 상세 정보를 성공적으로 조회했습니다.", serializer.data)

    # @swagger_auto_schema(
    #     tags=["schedule"],
    #     operation_summary="스케줄 수정",
    #     operation_description="특정 스케줄의 정보를 부분 업데이트합니다.",
    #     request_body=ScheduleSerializer,
    #     responses={
    #         200: ScheduleUpdateResponseSerializer(),
    #         400: ErrorResponseSerializer()
    #     }
    # )
    # def patch(self, request, *args, **kwargs):
    #     # Check for admin or moderator permission manually
    #     if not (request.user.is_staff or request.user.groups.filter(name="moderator").exists()):
    #         return self.create_response(403, "스케줄 수정 권한이 없습니다.", None, status.HTTP_403_FORBIDDEN)
    #     instance = self.get_object()
    #     serializer = self.serializer_class(instance, data=request.data, partial=True)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return self.create_response(200, "스케줄이 성공적으로 수정되었습니다.", serializer.data)
    #     return self.create_response(400, "스케줄 수정에 실패했습니다.", serializer.errors, status.HTTP_400_BAD_REQUEST)

    # @swagger_auto_schema(
    #     tags=["schedule"],
    #     operation_summary="스케줄 삭제",
    #     operation_description="특정 스케줄을 삭제합니다.",
    #     responses={200: ScheduleDeleteResponseSerializer()}
    # )
    # def delete(self, request, *args, **kwargs):
    #     # Check for admin or moderator permission manually
    #     if not (request.user.is_staff or request.user.groups.filter(name="moderator").exists()):
    #         return self.create_response(403, "스케줄 삭제 권한이 없습니다.", None, status.HTTP_403_FORBIDDEN)
    #     instance = self.get_object()
    #     instance.delete()
    #     return self.create_response(200, "스케줄이 성공적으로 삭제되었습니다.", None)

# ── AttendanceListView: 출석 목록 조회 ──
class AttendanceListView(BaseResponseMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    serializer_class = AttendanceSerializer

    @swagger_auto_schema(
        tags=["attendance"],
        operation_summary="출석 목록 조회",
        operation_description="특정 스케줄의 출석 목록을 조회합니다.",
        responses={200: AttendanceListResponseSerializer()}
    )
    def get(self, request, *args, **kwargs):
        schedule_id = self.kwargs.get('schedule_id')
        if request.user.is_staff or request.user.groups.filter(name="moderator").exists():
            queryset = Attendance.objects.filter(schedule_id=schedule_id)
        else:
            queryset = Attendance.objects.filter(schedule_id=schedule_id, user=request.user)
        serializer = self.serializer_class(queryset, many=True)
        return self.create_response(200, "출석 목록을 성공적으로 조회했습니다.", serializer.data)

# ── AttendanceDetailView: 출석 상세 조회 및 업데이트 ──
class AttendanceDetailView(BaseResponseMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    serializer_class = AttendanceSerializer

    def get_object(self):
        schedule_id = self.kwargs.get('schedule_id')
        user_id = self.kwargs.get('user_id')
        # 관리자나 모더레이터는 user_id에 따른 출석 정보를 조회하고,
        # 일반 사용자는 자신의 출석 정보만 조회합니다.
        if self.request.user.is_staff or self.request.user.groups.filter(name="moderator").exists():
            return get_object_or_404(Attendance, schedule_id=schedule_id, user_id=user_id)
        else:
            return get_object_or_404(Attendance, schedule_id=schedule_id, user_id=self.request.user.id)

    @swagger_auto_schema(
        tags=["attendance"],
        operation_summary="출석 상세 조회",
        operation_description="특정 사용자의 출석 상세 정보를 조회합니다.",
        responses={200: AttendanceDetailResponseSerializer()}
    )
    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.serializer_class(instance, context={'request': request})
        return self.create_response(200, "출석 상세 정보를 성공적으로 조회했습니다.", serializer.data)

    @swagger_auto_schema(
        tags=["attendance"],
        operation_summary="출석 업데이트",
        operation_description="출석 정보를 부분 수정합니다. (스케줄 시작~종료 시간 내에만 업데이트 가능)",
        request_body=AttendanceSerializer,
        responses={
            200: AttendanceUpdateResponseSerializer(),
            400: ErrorResponseSerializer()
        }
    )
    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        schedule = instance.schedule
        if not (schedule.start_time <= now() <= schedule.end_time):
            return self.create_response(400, "현재 출석을 등록할 수 없는 시간입니다.", None, status.HTTP_400_BAD_REQUEST)
        serializer = self.serializer_class(instance, data=request.data, context={'request': request}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return self.create_response(200, "출석이 성공적으로 업데이트되었습니다.", serializer.data)
        return self.create_response(400, "출석 업데이트에 실패했습니다.", serializer.errors, status.HTTP_400_BAD_REQUEST)
