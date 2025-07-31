from rest_framework import serializers
from .serializers import ScheduleSerializer

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
