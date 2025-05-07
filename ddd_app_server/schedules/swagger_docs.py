from rest_framework import permissions, status, serializers
from .serializers import ScheduleSerializer, AttendanceSerializer

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
