from rest_framework import serializers
from .models import Schedule
from profiles.models import Profile
from attendances.models import Attendance
from profiles.serializers import ProfileSummarySerializer


class AttendanceSummarySerializer(serializers.ModelSerializer):
    profile = ProfileSummarySerializer(source='user.profile', read_only=True)

    class Meta:
        model = Attendance
        fields = ['profile', 'status', 'updated_at', 'method', 'note']
        read_only_fields = fields


class ScheduleSerializer(serializers.ModelSerializer):
    attendances_summary = serializers.SerializerMethodField()

    class Meta:
        model = Schedule
        fields = ['id', 'title', 'description', 'start_time', 'end_time', 'created_at', 'attendances_summary']
        read_only_fields = ['id', 'created_at', 'attendances_summary']

    def get_attendances_summary(self, obj):
        """
        Returns a summary of attendances related to the schedule.
        """
        attendances = obj.attendances.all()  # Assuming a reverse relation named 'attendances'
        return AttendanceSummarySerializer(attendances, many=True).data

    def validate(self, data):
        if data.get('end_time') and data.get('start_time') and data['end_time'] <= data['start_time']:
            raise serializers.ValidationError("종료 시간은 시작 시간보다 이후여야 합니다.")
        return data
