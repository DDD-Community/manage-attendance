from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import Schedule, Attendance
from .serializers import ScheduleSerializer, AttendanceSerializer
from django.views.decorators.csrf import csrf_exempt

class ScheduleListView(APIView):
    """
    /schedules/
    GET: 스케쥴 목록 조회
    """
    permission_classes = [permissions.IsAuthenticated]

    @csrf_exempt
    def get(self, request, *args, **kwargs):
        """
        스케쥴 목록을 조회합니다.
        """
        # 모든 스케쥴 불러오기
        # schedules = Schedule.objects.all()
        # serializer = ScheduleSerializer(schedules, many=True)

        # 실제 동작 예시(시리얼라이저 없이)
        # 데이터베이스 연동이 없으므로 목업 데이터만 반환
        mock_schedules = [
            {
                "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
                "title": "직군 세션2",
                "description": "커리큘럼에 대한 설명 문구 작성",
                "start_time": "2023-01-01T10:00:00Z",
                "end_time": "2023-01-01T12:00:00Z",
            },
            {
                "id": "c56a4180-65aa-42ec-a945-5fd21dec0538",
                "title": "기수 전체 OT",
                "description": "전체 오리엔테이션",
                "start_time": "2023-01-10T10:00:00Z",
                "end_time": "2023-01-10T12:00:00Z",
            }
        ]

        return Response({
            "code": 200,
            "message": "스케쥴 목록 조회 성공",
            "data": mock_schedules  # 실제 구현 시에는 serializer.data 사용
        }, status=status.HTTP_200_OK)


class ScheduleDetailView(APIView):
    """
    /schedules/{schedule_id}/
    GET: 특정 스케쥴 상세 조회
    PATCH: 특정 스케쥴 수정
    DELETE: 특정 스케쥴 삭제
    """
    permission_classes = [permissions.IsAuthenticated]

    @csrf_exempt
    def get_object(self, schedule_id):
        # UUID가 아닌 "now" 같은 특별 케이스도 처리하고 싶다면 분기 처리를 추가할 수 있습니다.
        # if schedule_id == "now":
        #     # 예: 현재 진행 중인 스케쥴을 찾아 반환하는 로직
        #     return ...
        # return get_object_or_404(Schedule, pk=schedule_id)

        # 여기서는 단순 get_object_or_404 로직 예시
        # schedule = get_object_or_404(Schedule, pk=schedule_id)
        # return schedule
        return None  # 실제 코드에서는 Schedule 객체 반환

    @csrf_exempt
    def get(self, request, schedule_id, *args, **kwargs):
        """
        특정 스케쥴의 세부 정보를 조회합니다.
        """
        # schedule = self.get_object(schedule_id)
        # serializer = ScheduleSerializer(schedule)

        # 목업 데이터 예시
        mock_schedule_detail = {
            "title": "직군 세션2",
            "description": "커리큘럼에 대한 설명 문구 작성",
            "start_time": "2023-01-01T10:00:00Z",
            "end_time": "2023-01-01T12:00:00Z",
        }

        return Response({
            "code": 200,
            "message": "스케쥴 상세조회 성공",
            "data": mock_schedule_detail  # 실제 구현 시에는 serializer.data 사용
        }, status=status.HTTP_200_OK)

    @csrf_exempt
    def patch(self, request, schedule_id, *args, **kwargs):
        """
        특정 스케쥴의 정보를 수정합니다.
        """
        # schedule = self.get_object(schedule_id)
        # serializer = ScheduleSerializer(schedule, data=request.data, partial=True)
        #
        # if serializer.is_valid():
        #     serializer.save()
        #     return Response({
        #         "code": 200,
        #         "message": "스케쥴 수정 성공",
        #         "data": {}
        #     }, status=status.HTTP_200_OK)
        #
        # return Response({
        #     "code": 400,
        #     "message": "잘못된 요청 데이터",
        #     "data": serializer.errors
        # }, status=status.HTTP_400_BAD_REQUEST)

        # 목업 응답
        return Response({
            "code": 200,
            "message": "스케쥴 수정 성공",
            "data": {}
        }, status=status.HTTP_200_OK)

    @csrf_exempt
    def delete(self, request, schedule_id, *args, **kwargs):
        """
        특정 스케쥴을 삭제합니다.
        """
        # schedule = self.get_object(schedule_id)
        # schedule.delete()

        return Response({
            "code": 200,
            "message": "스케쥴 삭제 성공",
            "data": {}
        }, status=status.HTTP_200_OK)


class AttendanceListView(APIView):
    """
    /schedules/{schedule_id}/attendances/
    GET: 특정 스케줄의 출석 현황 조회
    """
    permission_classes = [permissions.IsAuthenticated]

    @csrf_exempt
    def get(self, request, schedule_id, *args, **kwargs):
        """
        특정 스케줄의 출석 현황을 조회합니다.
        """
        # schedule = get_object_or_404(Schedule, pk=schedule_id)
        # attendances = Attendance.objects.filter(schedule=schedule)
        #
        # attendance_count = attendances.filter(attendance_status="present").count()
        # late_count = attendances.filter(attendance_status="late").count()
        # absent_count = attendances.filter(attendance_status="absent").count()
        #
        # serializer = AttendanceSerializer(attendances, many=True)

        # 목업 데이터 예시
        mock_data = {
            "attendance_count": 10,
            "late_count": 2,
            "absent_count": 1,
            "members": [
                {
                    "name": "김디디",
                    "tags": ["role:member", "position:designer", "team:ios2", "generation:11기"],
                    "attendance_status": "present",
                    "note": ""
                },
                {
                    "name": "이챗GPT",
                    "tags": ["role:member", "position:developer", "team:backend", "generation:10기"],
                    "attendance_status": "late",
                    "note": "버스 연착"
                }
            ]
        }

        return Response({
            "code": 200,
            "message": "출석 현황 조회 성공",
            "data": mock_data  # 실제 구현 시에는 serializer.data를 포함한 통계 처리
        }, status=status.HTTP_200_OK)


class AttendanceDetailView(APIView):
    """
    /schedules/{schedule_id}/attendances/{user_id}/
    PATCH: 특정 스케줄의 특정 유저 출석 상태 수정
    """
    permission_classes = [permissions.IsAuthenticated]

    @csrf_exempt
    def patch(self, request, schedule_id, user_id, *args, **kwargs):
        """
        특정 스케줄의 특정 유저 출석 상태를 수정합니다.
        """
        # schedule = get_object_or_404(Schedule, pk=schedule_id)
        # attendance = get_object_or_404(Attendance, schedule=schedule, user__id=user_id)
        #
        # serializer = AttendanceSerializer(attendance, data=request.data, partial=True)
        # if serializer.is_valid():
        #     serializer.save()
        #     return Response({
        #         "code": 200,
        #         "message": "출석 수정 성공",
        #         "data": {}
        #     }, status=status.HTTP_200_OK)
        # return Response({
        #     "code": 400,
        #     "message": "잘못된 요청 데이터",
        #     "data": serializer.errors
        # }, status=status.HTTP_400_BAD_REQUEST)

        # 목업 응답
        return Response({
            "code": 200,
            "message": "출석 수정 성공",
            "data": {}
        }, status=status.HTTP_200_OK)
