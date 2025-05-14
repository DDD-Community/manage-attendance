from datetime import datetime

# Python Standard Libraries & Django Imports
from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db.models import Count, Q, Case, When, IntegerField

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
from schedules.models import Schedule
from .models import Attendance
from .serializers import AttendanceSerializer, AttendanceCountSerializer
from .swagger_docs import (
    AttendanceListResponseSerializer,
    # AttendanceCreateResponseSerializer,
    AttendanceDetailResponseSerializer,
    AttendanceUpdateResponseSerializer,
    # AttendanceDeleteResponseSerializer
)

# Get the User model
User = get_user_model()

# ── AttendanceListView: 출석 목록 조회 (Query Param Filtering) ──
class AttendanceListView(BaseResponseMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    serializer_class = AttendanceSerializer

    @swagger_auto_schema(
        tags=["attendance"],
        operation_summary="출석 목록 조회",
        operation_description="""
        출석 목록을 조회합니다. 
        쿼리 파라미터 'user_id' 또는 'schedule_id'를 사용하여 필터링할 수 있습니다.
        스태프 사용자는 모든 출석 기록을 대상으로 필터링하며, 일반 사용자는 자신의 출석 기록 내에서 필터링합니다.
        """,
        manual_parameters=[
            openapi.Parameter('user_id', openapi.IN_QUERY, description="필터링할 사용자의 ID", type=openapi.TYPE_INTEGER),
            openapi.Parameter('schedule_id', openapi.IN_QUERY, description="필터링할 스케줄의 ID", type=openapi.TYPE_INTEGER),
        ],
        responses={
            200: AttendanceListResponseSerializer(),
            400: ErrorResponseSerializer()
        }
    )
    def get(self, request, *args, **kwargs):
        user_id_filter = request.query_params.get('user_id')
        schedule_id_filter = request.query_params.get('schedule_id')

        # 기본 쿼리셋: 스태프는 전체, 일반 사용자는 자신 것만
        if request.user.is_staff:
            base_queryset = Attendance.objects.select_related('user', 'schedule').all() # Optimization
        else:
            base_queryset = Attendance.objects.select_related('user', 'schedule').filter(user=request.user)

        filtered_queryset = base_queryset
        try:
            # Schedule ID 필터링 (모든 사용자 가능)
            if schedule_id_filter:
                filtered_queryset = filtered_queryset.filter(schedule__id=int(schedule_id_filter))

            # User ID 필터링
            if user_id_filter:
                user_id_to_filter = int(user_id_filter)
                if request.user.is_staff:
                    # 스태프는 모든 사용자로 필터링 가능
                    filtered_queryset = filtered_queryset.filter(user__id=user_id_to_filter)
                else:
                    # 일반 사용자는 오직 자신의 ID로만 필터링 가능 (사실상 base_queryset 에서 이미 처리됨)
                    if user_id_to_filter != request.user.id:
                         return self.create_response(403, "다른 사용자의 출석 목록을 조회할 권한이 없습니다.", None, status.HTTP_403_FORBIDDEN)

        except ValueError:
            return self.create_response(400, "잘못된 user_id 또는 schedule_id 형식입니다.", None, status.HTTP_400_BAD_REQUEST)
        except Schedule.DoesNotExist: # 만약 schedule_id 로 필터링 시 존재하지 않는 경우
             return self.create_response(404, "해당 스케줄을 찾을 수 없습니다.", None, status.HTTP_404_NOT_FOUND)
        except User.DoesNotExist: # 만약 user_id 로 필터링 시 존재하지 않는 경우
             return self.create_response(404, "해당 사용자를 찾을 수 없습니다.", None, status.HTTP_404_NOT_FOUND)


        attendances = filtered_queryset.distinct()
        serializer = self.serializer_class(attendances, many=True, context={"request": request})
        return self.create_response(200, "출석 목록을 성공적으로 조회했습니다.", serializer.data)


# ── AttendanceDetailView: 출석 상세 조회, 수정, 삭제 ──
class AttendanceDetailView(BaseResponseMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    serializer_class = AttendanceSerializer

    # Helper method to get attendance object and check base permissions
    def get_object_and_check_permission(self, request, attendance_id, check_time=False):
        """
        Fetches the Attendance object, related user/schedule, and performs initial permission checks.
        Returns the attendance object or raises PermissionDenied/NotFound exceptions.
        Optionally checks time constraints.
        """
        try:
            # Fetch attendance with related user and schedule efficiently
            attendance = get_object_or_404(
                Attendance.objects.select_related('user', 'schedule'),
                pk=attendance_id
            )

            # Permission Check: Is the requester the owner or staff?
            is_owner = (attendance.user == request.user)
            is_staff = request.user.is_staff

            if not (is_owner or is_staff):
                raise permissions.PermissionDenied("이 출석 정보에 접근할 권한이 없습니다.")

            # Optional Time Constraint Check (for PATCH/DELETE, maybe?)
            if check_time and not is_staff: # Staff bypasses time check
                current_time = now()
                schedule = attendance.schedule
                if not (schedule.start_time <= current_time <= schedule.end_time):
                    # Use a specific exception or return a specific response maybe?
                    # For now, let's raise PermissionDenied for timing issues too for simplicity in helper
                    # Or maybe a different error like ValidationError? Let's stick to PermissionDenied for now.
                    raise permissions.PermissionDenied("현재 이 작업을 수행할 수 없는 시간입니다.")

            return attendance

        except Attendance.DoesNotExist:
            # This exception will be implicitly handled by get_object_or_404,
            # but keeping explicit except block for clarity if needed later.
            # We re-raise it here so the main methods can catch it if desired,
            # but get_object_or_404 already raises Http404.
            # Let get_object_or_404 handle the 404 response directly.
             raise # Re-raise the Http404 from get_object_or_404


    @swagger_auto_schema(
        tags=["attendance"],
        operation_summary="출석 상세 조회 (ID 기준)",
        operation_description="특정 ID를 가진 출석 상세 정보를 조회합니다. 본인 또는 스태프만 조회 가능합니다.",
        responses={
            200: AttendanceDetailResponseSerializer(),
            403: ErrorResponseSerializer(),
            404: ErrorResponseSerializer()
        }
    )
    def get(self, request, attendance_id, *args, **kwargs):
        attendance = self.get_object_and_check_permission(request, attendance_id)
        serializer = self.serializer_class(attendance, context={"request": request})
        return self.create_response(200, "출석 상세 정보를 성공적으로 조회했습니다.", serializer.data)


    @swagger_auto_schema(
        tags=["attendance"],
        operation_summary="출석 수정 (ID 기준)",
        operation_description="""
        특정 ID를 가진 출석 정보를 수정합니다.
        본인 또는 스태프만 수정 가능하며, 스케줄 진행 시간 내에만 가능합니다 (스태프 제외).
        """,
        request_body=AttendanceSerializer,
        responses={
            200: AttendanceUpdateResponseSerializer(),
            400: ErrorResponseSerializer(),
            403: ErrorResponseSerializer(),
            404: ErrorResponseSerializer()
        }
    )
    def patch(self, request, attendance_id, *args, **kwargs):
        # Check time constraint during fetch for PATCH
        attendance = self.get_object_and_check_permission(request, attendance_id, check_time=True)

        # 데이터 유효성 검사 및 수정 (partial=True 로 부분 업데이트 허용)
        serializer = self.serializer_class(attendance, data=request.data, partial=True, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return self.create_response(200, "출석 정보가 성공적으로 수정되었습니다.", serializer.data)
        else:
            return self.create_response(400, "출석 수정에 실패했습니다.", serializer.errors, status.HTTP_400_BAD_REQUEST)

    # @swagger_auto_schema(
    #     tags=["attendance"],
    #     operation_summary="출석 삭제",
    #     operation_description="특정 출석을 삭제합니다.",
    #     responses={
    #         204: openapi.Response(description="출석 정보가 성공적으로 삭제되었습니다."),
    #         403: ErrorResponseSerializer(),
    #         404: ErrorResponseSerializer()
    #     }
    # )
    # def delete(self, request, attendance_id, *args, **kwargs):
    #     # Time constraint check is optional for delete, let's omit it here (check_time=False)
    #     attendance = self.get_object_and_check_permission(request, attendance_id, check_time=False)
    #     attendance.delete()

    #     # Return 204 No Content (standard REST practice)
    #     return self.create_response(204, "출석이 성공적으로 삭제되었습니다.", None)


class AttendanceCountView(BaseResponseMixin, APIView):
    """
    Provides counts of attendance records based on status,
    filterable by user, group, schedule, and date range.
    """
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @swagger_auto_schema(
        tags=["attendance"],
        operation_summary="출석 카운트",
        operation_description="""
        출석 상태에 따른 카운트를 가져옵니다.
        user_id, group_id, schedule_id, start_date, end_date 등으로 필터가 가능합니다.
        """,
        manual_parameters=[
            openapi.Parameter('user_id', openapi.IN_QUERY, description="Filter counts for a specific user ID.", type=openapi.TYPE_INTEGER),
            openapi.Parameter('group_id', openapi.IN_QUERY, description="Filter counts for users belonging to a specific group ID.", type=openapi.TYPE_INTEGER),
            openapi.Parameter('schedule_id', openapi.IN_QUERY, description="Filter counts for a specific schedule ID (UUID).", type=openapi.TYPE_STRING),
            openapi.Parameter('start_date', openapi.IN_QUERY, description="Filter counts on or after this date (YYYY-MM-DD).", type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
            openapi.Parameter('end_date', openapi.IN_QUERY, description="Filter counts on or before this date (YYYY-MM-DD).", type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
        ],
        responses={
            200: AttendanceCountSerializer(),
            400: ErrorResponseSerializer(),
            403: ErrorResponseSerializer(),
            404: ErrorResponseSerializer(),
        }
    )
    def get(self, request, *args, **kwargs):
        # --- 1. Get Filter Parameters ---
        user_id_filter = request.query_params.get('user_id')
        group_id_filter = request.query_params.get('group_id')
        schedule_id_filter = request.query_params.get('schedule_id')
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')

        # --- 2. Base Queryset based on Permissions ---
        if request.user.is_staff:
            base_queryset = Attendance.objects.all()
        else:
            base_queryset = Attendance.objects.filter(user=request.user)

        filtered_queryset = base_queryset

        # --- 3. Apply Filters ---
        try:
            # User ID Filter
            if user_id_filter:
                user_id_to_filter = int(user_id_filter)
                if (user_id_to_filter != request.user.id) and (not request.user.is_staff):
                    return self.create_response(403, "You do not have permission to view counts for this user.", None, status.HTTP_403_FORBIDDEN)
                filtered_queryset = filtered_queryset.filter(user__id=user_id_to_filter)

            # Group ID Filter
            if group_id_filter:
                 group_id_to_filter = int(group_id_filter)
                 try:
                     target_group = Group.objects.get(pk=group_id_to_filter)
                     filtered_queryset = filtered_queryset.filter(user__groups=target_group)
                 except Group.DoesNotExist:
                      return self.create_response(404, f"Group with ID {group_id_to_filter} not found.", None, status.HTTP_404_NOT_FOUND)

            # Schedule ID Filter
            if schedule_id_filter:
                filtered_queryset = filtered_queryset.filter(schedule__id=schedule_id_filter)

            # Date Range Filters (apply to the schedule's start_time and end_time fields)
            if start_date_str:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                filtered_queryset = filtered_queryset.filter(schedule__start_time__date__gte=start_date)

            if end_date_str:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
                filtered_queryset = filtered_queryset.filter(schedule__end_time__date__lte=end_date)

        except ValueError as e:
            # Handle invalid integer conversion or date format
            error_msg = "Invalid filter value provided. Ensure IDs are integers and dates are YYYY-MM-DD."
            # Be more specific based on the error if possible
            if 'date' in str(e):
                 error_msg = "Invalid date format. Please use YYYY-MM-DD."
            return self.create_response(400, error_msg, None, status.HTTP_400_BAD_REQUEST)
        except Exception as e: # Catch other potential errors during filtering
            # Log the error e
            print(f"Error during filtering: {e}") # Replace with proper logging
            return self.create_response(500, "An error occurred while applying filters.", None, status.HTTP_500_INTERNAL_SERVER_ERROR)


        # --- 4. Perform Aggregation ---
        counts = filtered_queryset.aggregate(
            attendance_count=Count('id'),
            present_count=Count(Case(When(status='present', then=1), output_field=IntegerField())),
            late_count=Count(Case(When(status='late', then=1), output_field=IntegerField())),
            absent_count=Count(Case(When(status='absent', then=1), output_field=IntegerField())),
            exception_count=Count(Case(When(status='exception', then=1), output_field=IntegerField())),
            tbd_count=Count(Case(When(status='tbd', then=1), output_field=IntegerField())),
        )

        # --- 5. Serialize and Return ---
        serializer = AttendanceCountSerializer(data=counts)
        serializer.is_valid(raise_exception=True)
        return self.create_response(200, "Attendance counts retrieved successfully.", counts)
