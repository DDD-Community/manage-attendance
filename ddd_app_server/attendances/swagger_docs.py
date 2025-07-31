from rest_framework import serializers
from .serializers import AttendanceSerializer

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
