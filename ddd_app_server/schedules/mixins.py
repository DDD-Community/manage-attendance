from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from rest_framework.exceptions import NotFound
from .models import Schedule

class CurrentScheduleMixin:
    def get_schedule(self, schedule_id):
        if schedule_id == 'now':
            current_time = now()
            schedule = Schedule.objects.filter(
                start_time__lte=current_time,
                end_time__gte=current_time
            ).first()
            if not schedule:
                raise NotFound(detail="현재 진행 중인 스케줄이 없습니다.")
            return schedule
        return get_object_or_404(Schedule, id=schedule_id)
