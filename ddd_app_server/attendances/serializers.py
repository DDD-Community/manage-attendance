from rest_framework import serializers
from .models import Attendance
from profiles.models import Profile
from schedules.models import Schedule
from profiles.serializers import ProfileSummarySerializer
from datetime import timedelta
from django.utils.timezone import now


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
        profile = getattr(obj.user, 'profile', None)
        if profile:
            return ProfileSummarySerializer(profile).data
        return None

    def get_schedule_summary(self, obj):
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

    def update(self, instance, validated_data):
        # Get the status from validated_data, default to the instance's current status
        status_value = validated_data.get('status', instance.status)

        # If status is 'auto', determine the status based on time
        if status_value == 'auto':
            current_time = now()
            schedule = instance.schedule
            start_time = schedule.start_time
            if start_time - timedelta(hours=1) <= current_time <= start_time + timedelta(minutes=10):
                instance.status = 'present'
            elif start_time + timedelta(minutes=10) < current_time <= start_time + timedelta(minutes=60):
                instance.status = 'late'
            elif current_time > start_time + timedelta(minutes=60):
                instance.status = 'absent'
            else:
                instance.status = 'tbd'
        else:
            # Otherwise, just update the status from validated_data
            instance.status = status_value

        # Update other fields if they are in validated_data
        instance.method = validated_data.get('method', instance.method)
        instance.note = validated_data.get('note', instance.note)

        instance.save()
        return instance


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
