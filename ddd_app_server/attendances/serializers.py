from rest_framework import serializers
from .models import Attendance
from profiles.models import Profile
from schedules.models import Schedule
from profiles.serializers import ProfileSummarySerializer


class ScheduleSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = ['id', 'title', 'description', 'start_time', 'end_time']
        read_only_fields = fields


class AttendanceSerializer(serializers.ModelSerializer):
    profile_summary = serializers.SerializerMethodField()
    schedule_summary = serializers.SerializerMethodField()

    class Meta:
        model = Attendance
        fields = ['id', 'profile_summary', 'schedule_summary', 'updated_at', 'status', 'method', 'note']
        read_only_fields = ['id', 'profile_summary', 'schedule_summary', 'updated_at']

    def get_profile_summary(self, obj):
        """
        Returns the serialized profile summary for the user.
        """
        if hasattr(obj, 'user') and hasattr(obj.user, 'profile'):
            return ProfileSummarySerializer(obj.user.profile).data
        return None

    def get_schedule_summary(self, obj):
        """
        Returns the serialized schedule summary.
        """
        if hasattr(obj, 'schedule'):
            return ScheduleSummarySerializer(obj.schedule).data
        return None

    def validate_status(self, value):
        if value not in dict(Attendance.ATTENDANCE_STATUS_CHOICES):
            raise serializers.ValidationError("유효하지 않은 출석 상태입니다.")
        return value

    def validate_method(self, value):
        if value and value not in dict(Attendance.METHOD_CHOICES):
            raise serializers.ValidationError("유효하지 않은 출석 방법입니다.")
        return value


class AttendanceCountSerializer(serializers.Serializer):
    """
    Serializer for representing attendance counts based on status.
    """
    attendance_count = serializers.IntegerField(default=0, help_text="Total number of attendance records matching the filters.")
    present_count = serializers.IntegerField(default=0, help_text="Number of 'present' records.")
    late_count = serializers.IntegerField(default=0, help_text="Number of 'late' records.")
    absent_count = serializers.IntegerField(default=0, help_text="Number of 'absent' records.")
    exception_count = serializers.IntegerField(default=0, help_text="Number of 'exception' records.")
    tbd_count = serializers.IntegerField(default=0, help_text="Number of 'tbd' (to be determined) records.")
