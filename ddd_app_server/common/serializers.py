from rest_framework import serializers

# 에러 응답용 Serializer (공통)
class ErrorResponseSerializer(serializers.Serializer):
    code = serializers.IntegerField()
    message = serializers.CharField()
    data = serializers.JSONField(allow_null=True)
