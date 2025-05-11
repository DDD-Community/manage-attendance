from django.utils.timezone import now
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, status
from rest_framework.views import APIView
from common.mixins import BaseResponseMixin
from common.serializers import ErrorResponseSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializers import ScheduleSerializer, AttendanceSerializer
from .models import Schedule, Attendance
from .mixins import CurrentScheduleMixin, CurrentScheduleAndUserMixin
from .swagger_docs import (
    ScheduleListResponseSerializer,
    ScheduleCreateResponseSerializer,
    ScheduleDetailResponseSerializer,
    ScheduleUpdateResponseSerializer,
    ScheduleDeleteResponseSerializer,
    AttendanceListResponseSerializer,
    AttendanceDetailResponseSerializer,
    AttendanceUpdateResponseSerializer
)
from django.db.models import Q


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
        if request.user.is_staff:
            # 스태프 사용자는 모든 스케줄을 조회
            schedules = Schedule.objects.all()
        else:
            # 일반 사용자는 자신과 관련된 스케줄만 조회
            schedules = Schedule.objects.filter(
                Q(assigned_users=request.user) | 
                Q(assigned_users__username=request.user.username) | 
                Q(assigned_groups__name__in=request.user.groups.values_list("name", flat=True))
            ).distinct()
        serializer = self.serializer_class(schedules, many=True, context={"request": request})
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
class ScheduleDetailView(BaseResponseMixin, CurrentScheduleMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    serializer_class = ScheduleSerializer

    @swagger_auto_schema(
        tags=["schedule"],
        operation_summary="스케줄 상세 조회",
        operation_description="특정 스케줄의 상세 정보를 조회합니다.",
        responses={200: ScheduleDetailResponseSerializer()}
    )
    def get(self, request, *args, **kwargs):
        schedule_id = self.kwargs.get("schedule_id")
        schedule = self.get_schedule(schedule_id)
        serializer = self.serializer_class(schedule, context={"request": request})
        return self.create_response(200, "스케줄 상세 정보를 성공적으로 조회했습니다.", serializer.data)

    @swagger_auto_schema(
        tags=["schedule"],
        operation_summary="스케줄 수정",
        operation_description="특정 스케줄의 정보를 부분 업데이트합니다.",
        request_body=ScheduleSerializer,
        responses={
            200: ScheduleUpdateResponseSerializer(),
            400: ErrorResponseSerializer()
        }
    )
    def patch(self, request, *args, **kwargs):
        # Check for admin or moderator permission manually
        if not (request.user.is_staff or request.user.groups.filter(name="moderator").exists()):
            return self.create_response(403, "스케줄 수정 권한이 없습니다.", None, status.HTTP_403_FORBIDDEN)
        schedule_id = self.kwargs.get("schedule_id")
        schedule = self.get_schedule(schedule_id)
        serializer = self.serializer_class(schedule, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return self.create_response(200, "스케줄이 성공적으로 수정되었습니다.", serializer.data)
        return self.create_response(400, "스케줄 수정에 실패했습니다.", serializer.errors, status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        tags=["schedule"],
        operation_summary="스케줄 삭제",
        operation_description="특정 스케줄을 삭제합니다.",
        responses={200: ScheduleDeleteResponseSerializer()}
    )
    def delete(self, request, *args, **kwargs):
        # Check for admin or moderator permission manually
        if not (request.user.is_staff or request.user.groups.filter(name="moderator").exists()):
            return self.create_response(403, "스케줄 삭제 권한이 없습니다.", None, status.HTTP_403_FORBIDDEN)
        schedule_id = self.kwargs.get("schedule_id")
        schedule = self.get_schedule(schedule_id)
        schedule.delete()
        return self.create_response(200, "스케줄이 성공적으로 삭제되었습니다.", None)


# ── AttendanceListView: 출석 목록 조회 ──
class AttendanceListView(BaseResponseMixin, CurrentScheduleMixin, APIView):
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
        schedule_id = self.kwargs.get("schedule_id")
        schedule = self.get_schedule(schedule_id)

        if request.user.is_staff or request.user.groups.filter(name="moderator").exists():
            queryset = Attendance.objects.filter(schedule=schedule)
        else:
            queryset = Attendance.objects.filter(schedule=schedule, user=request.user)
        serializer = self.serializer_class(queryset, many=True)
        return self.create_response(200, "출석 목록을 성공적으로 조회했습니다.", serializer.data)


# ── AttendanceDetailView: 출석 상세 조회 및 업데이트 ──
class AttendanceDetailView(BaseResponseMixin, CurrentScheduleAndUserMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    serializer_class = AttendanceSerializer

    @swagger_auto_schema(
        tags=["attendance"],
        operation_summary="출석 상세 조회",
        operation_description="특정 사용자의 출석 상세 정보를 조회합니다.",
        responses={200: AttendanceDetailResponseSerializer()}
    )
    def get(self, request, *args, **kwargs):
        user_id = self.kwargs.get("user_id")
        schedule_id = self.kwargs.get("schedule_id")
        schedule, user = self.get_schedule_and_user(schedule_id, user_id)

        if user != self.request.user and (not self.request.user.is_staff):
            return self.create_response(403, "다른 사용자의 출석 정보를 조회할 수 없습니다.", None, status.HTTP_403_FORBIDDEN)

        attendance = get_object_or_404(Attendance, schedule=schedule, user=user)
        serializer = self.serializer_class(attendance, context={"request": request})
        return self.create_response(200, "출석 상세 정보를 성공적으로 조회했습니다.", serializer.data)

    @swagger_auto_schema(
        tags=["attendance"],
        operation_summary="출석 생성",
        operation_description="새로운 출석 정보를 생성합니다.",
        request_body=AttendanceSerializer,
        responses={
            201: AttendanceUpdateResponseSerializer(),
            400: ErrorResponseSerializer()
        }
    )
    def post(self, request, *args, **kwargs):
        user_id = self.kwargs.get("user_id")
        schedule_id = self.kwargs.get("schedule_id")
        schedule, user = self.get_schedule_and_user(schedule_id, user_id)

        # Ensure the current time is within the schedule's start and end time
        if not (schedule.start_time <= now() <= schedule.end_time) and (not self.request.user.is_staff):
            return self.create_response(400, "현재 출석을 등록할 수 없는 시간입니다.", None, status.HTTP_400_BAD_REQUEST)

        # Ensure the user has permission to update the attendance
        if user != self.request.user and (not self.request.user.is_staff):
            return self.create_response(403, "다른 사용자의 출석 정보를 등록할 수 없습니다.", None, status.HTTP_403_FORBIDDEN)

        # Create a new attendance record
        serializer = self.serializer_class(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save(schedule=schedule, user=user)
            return self.create_response(201, "새로운 출석이 성공적으로 생성되었습니다.", serializer.data, status.HTTP_201_CREATED)
        return self.create_response(400, "출석 생성에 실패했습니다.", serializer.errors, status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        tags=["attendance"],
        operation_summary="출석 수정",
        operation_description="특정 사용자의 출석 정보를 수정합니다.",
        request_body=AttendanceSerializer,
        responses={
            200: AttendanceUpdateResponseSerializer(),
            400: ErrorResponseSerializer()
        }
    )
    def patch(self, request, *args, **kwargs):
        user_id = self.kwargs.get("user_id")
        schedule_id = self.kwargs.get("schedule_id")
        schedule, user = self.get_schedule_and_user(schedule_id, user_id)

        # Ensure the current time is within the schedule's start and end time
        if not (schedule.start_time <= now() <= schedule.end_time) and (not self.request.user.is_staff):
            return self.create_response(400, "현재 출석을 수정할 수 없는 시간입니다.", None, status.HTTP_400_BAD_REQUEST)

        # Ensure the user has permission to update the attendance
        if user != self.request.user and (not self.request.user.is_staff):
            return self.create_response(403, "다른 사용자의 출석 정보를 수정할 수 없습니다.", None, status.HTTP_403_FORBIDDEN)

        attendance = get_object_or_404(Attendance, schedule=schedule, user=user)
        serializer = self.serializer_class(attendance, data=request.data, partial=True, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return self.create_response(200, "출석 정보가 성공적으로 수정되었습니다.", serializer.data)
        return self.create_response(400, "출석 수정에 실패했습니다.", serializer.errors, status.HTTP_400_BAD_REQUEST)
