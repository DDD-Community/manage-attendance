from rest_framework import serializers
from .models import Schedule, Attendance
from profiles.models import Profile
from profiles.serializers import ProfileSerializer

class ScheduleSerializer(serializers.ModelSerializer):
    attendance = serializers.SerializerMethodField()

    class Meta:
        model = Schedule
        fields = ['id', 'title', 'description', 'start_time', 'end_time', 'created_at', 'attendance']
        read_only_fields = ['id', 'created_at']

    def validate(self, data):
        if data.get('end_time') and data.get('start_time') and data['end_time'] <= data['start_time']:
            raise serializers.ValidationError("종료 시간은 시작 시간보다 이후여야 합니다.")
        return data

    def get_attendance(self, instance):
        request = self.context.get('request')
        if not request or not hasattr(request, 'user'):
            return None  # Return None if the request or user is not available

        user = request.user
        attendance = Attendance.objects.filter(schedule=instance, user=user).first()
        if attendance:
            return {
                'status': attendance.status,
                'method': attendance.method,
                'note': attendance.note,
                'updated_at': attendance.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
            }
        return None

class ProfileSummarySerializer(ProfileSerializer):
    class Meta:
        model = Profile
        fields = ['name', 'role', 'team', 'cohort']

class AttendanceSerializer(serializers.ModelSerializer):
    schedule_title = serializers.ReadOnlyField(source='schedule.title')
    profile = ProfileSummarySerializer(source='user.profile', read_only=True)
    user_id = serializers.ReadOnlyField(source='user.id')
    schedule_id = serializers.ReadOnlyField(source='schedule.id')

    class Meta:
        model = Attendance
        fields = ['id', 'profile', 'schedule_title',
                 'status', 'updated_at', 'method', 'note', 'user_id', 'schedule_id']
        read_only_fields = ['id', 'profile', 'schedule_title', 'updated_at', 'user_id', 'schedule_id']

    def validate_status(self, value):
        if value not in dict(Attendance.ATTENDANCE_STATUS_CHOICES):
            raise serializers.ValidationError("유효하지 않은 출석 상태입니다.")
        return value

    def validate_method(self, value):
        if value and value not in dict(Attendance.METHOD_CHOICES):
            raise serializers.ValidationError("유효하지 않은 출석 방법입니다.")
        return value