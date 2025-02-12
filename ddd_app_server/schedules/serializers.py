from rest_framework import serializers
from .models import Schedule, Attendance

class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = ['id', 'title', 'description', 'start_time', 'end_time']


class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = ['id', 'user', 'attendance_status', 'method', 'note']
        # user 정보가 필요하다면, user에 대한 nested serializer 등을 추가
