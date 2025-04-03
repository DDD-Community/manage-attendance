from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Schedule, Attendance

class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = ['id', 'title', 'description', 'start_time', 'end_time', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate(self, data):
        if data.get('end_time') and data.get('start_time') and data['end_time'] <= data['start_time']:
            raise serializers.ValidationError("종료 시간은 시작 시간보다 이후여야 합니다.")
        return data

class AttendanceSerializer(serializers.ModelSerializer):
    schedule_title = serializers.ReadOnlyField(source='schedule.title')
    user_id = serializers.IntegerField(write_only=True, required=False)
    user_name = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Attendance
        fields = ['id', 'user', 'user_id', 'user_name', 'schedule', 'schedule_title', 
                 'status', 'updated_at', 'method', 'note']
        read_only_fields = ['id', 'user', 'user_id', 'schedule', 'schedule_title', 'user_name', 'updated_at']

    def validate(self, data):
        request = self.context.get('request')
        if not request:
            raise serializers.ValidationError("Request context is required")

        # Get user from URL or request
        user_id = self.context.get('user_id')
        if user_id:
            try:
                user = get_user_model().objects.get(id=user_id)
            except get_user_model().DoesNotExist:
                raise serializers.ValidationError("User does not exist")
        else:
            user = request.user

        # Check permissions
        if not (request.user.is_staff or request.user.groups.filter(name="moderator").exists()):
            if user != request.user:
                raise serializers.ValidationError("You can only update your own attendance")

        # Set user in data
        data['user'] = user
        return data

    def validate_status(self, value):
        if value not in dict(Attendance.ATTENDANCE_STATUS_CHOICES):
            raise serializers.ValidationError("유효하지 않은 출석 상태입니다.")
        return value

    def validate_method(self, value):
        if value and value not in dict(Attendance.METHOD_CHOICES):
            raise serializers.ValidationError("유효하지 않은 출석 방법입니다.")
        return value