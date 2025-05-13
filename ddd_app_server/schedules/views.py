from datetime import datetime

# Python Standard Libraries & Django Imports
from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from django.contrib.auth import get_user_model
from django.db.models import Q

# Third-party Library Imports
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

# Local Application/Library Specific Imports
from common.mixins import BaseResponseMixin
from common.serializers import ErrorResponseSerializer
from .mixins import CurrentScheduleMixin
from .models import Schedule
from .serializers import ScheduleSerializer
from .swagger_docs import (
    ScheduleListResponseSerializer,
    ScheduleCreateResponseSerializer,
    ScheduleDetailResponseSerializer,
    ScheduleUpdateResponseSerializer,
    ScheduleDeleteResponseSerializer,
)

# Get the User model
User = get_user_model()

# ── ScheduleListView: 스케줄 목록 조회 및 생성 ──
class ScheduleListView(BaseResponseMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    serializer_class = ScheduleSerializer

    @swagger_auto_schema(
        tags=["schedule"],
        operation_summary="스케줄 목록 조회",
        operation_description="""
        스케줄 목록을 조회합니다. 
        쿼리 파라미터 'user_id' 또는 'group_id'를 사용하여 특정 사용자 또는 그룹에 할당된 스케줄을 필터링할 수 있습니다.
        스태프 사용자는 모든 스케줄을 대상으로 필터링하며, 일반 사용자는 자신이 접근 가능한 스케줄 내에서 필터링합니다.
        """,
        manual_parameters=[
            openapi.Parameter('group_id', openapi.IN_QUERY, description="필터링할 그룹의 ID", type=openapi.TYPE_INTEGER),
            openapi.Parameter('date', openapi.IN_QUERY, description="필터링할 날짜 (YYYY-MM-DD)", type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE)
        ],
        responses={
            200: ScheduleListResponseSerializer(),
            400: ErrorResponseSerializer()
        }
    )
    def get(self, request, *args, **kwargs):
        group_id_filter = request.query_params.get('group_id')
        date_filter_str = request.query_params.get('date')

        # 기본 쿼리셋 결정 (스태프 vs 일반 사용자)
        if request.user.is_staff:
            # 스태프 사용자는 모든 스케줄을 기본 대상으로 함
            base_queryset = Schedule.objects.all()
        else:
            # 일반 사용자는 자신과 관련된 스케줄만 기본 대상으로 함
            # base_queryset = Schedule.objects.filter(
            #     Q(assigned_users=request.user) |
            #     Q(assigned_users__username=request.user.username) |
            #     Q(assigned_groups__in=request.user.groups.all()) # 그룹 필터링 방식 변경 (더 효율적일 수 있음)
            # ).distinct()
            base_queryset = Schedule.objects.filter(group__in=request.user.groups.all())
        
        target_date = None
        if date_filter_str:
            try:
                target_date = datetime.strptime(date_filter_str, '%Y-%m-%d').date()
            except ValueError:
                return self.create_response(400, "잘못된 날짜 형식입니다. 'YYYY-MM-DD' 형식을 사용해주세요.", None, status.HTTP_400_BAD_REQUEST)

        filtered_queryset = base_queryset
        try:
            # Group ID 필터링
            if group_id_filter:
                filtered_queryset = filtered_queryset.filter(assigned_groups__id=int(group_id_filter))

            # 날짜 필터링
            if target_date:
                filtered_queryset = filtered_queryset.filter(start_time__date=target_date)

        except ValueError:
             return self.create_response(400, "잘못된 group_id 입니다.", None, status.HTTP_400_BAD_REQUEST)


        schedules = filtered_queryset.distinct() 
        serializer = self.serializer_class(schedules, many=True, context={"request": request})
        return self.create_response(200, "스케줄 목록을 성공적으로 조회했습니다.", serializer.data)

    @swagger_auto_schema(
        tags=["schedule"],
        operation_summary="스케줄 생성",
        operation_description="새로운 스케줄을 생성합니다. 관리자 또는 moderator 그룹 사용자만 가능합니다.",
        request_body=ScheduleSerializer,
        responses={
            201: ScheduleCreateResponseSerializer(),
            400: ErrorResponseSerializer(),
            403: ErrorResponseSerializer() # 403 응답 추가
        }
    )
    def post(self, request, *args, **kwargs):
        # Check for admin or moderator permission manually
        if not request.user.is_staff:
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
    def get(self, request, schedule_id, *args, **kwargs):
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
    def patch(self, request, schedule_id, *args, **kwargs):
        # Check for admin or moderator permission manually
        if not request.user.is_staff:
            return self.create_response(403, "스케줄 수정 권한이 없습니다.", None, status.HTTP_403_FORBIDDEN)
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
    def delete(self, request, schedule_id, *args, **kwargs):
        # Check for admin or moderator permission manually
        if not request.user.is_staff:
            return self.create_response(403, "스케줄 삭제 권한이 없습니다.", None, status.HTTP_403_FORBIDDEN)
        schedule = self.get_schedule(schedule_id)
        schedule.delete()
        return self.create_response(204, "스케줄이 성공적으로 삭제되었습니다.", None)

