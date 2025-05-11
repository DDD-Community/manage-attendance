from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from rest_framework.exceptions import NotFound
from django.contrib.auth.models import User
from .models import Schedule

class CurrentScheduleMixin:
    def get_schedule(self, schedule_id):
        if schedule_id is None or schedule_id == "now":
            current_time = now()
            schedule = Schedule.objects.filter(
                start_time__lte=current_time,
                end_time__gte=current_time
            ).first()
            if not schedule:
                raise NotFound(detail="현재 진행 중인 스케줄이 없습니다.")
            return schedule
        return get_object_or_404(Schedule, id=schedule_id)

class CurrentUserMixin:
    def get_user(self, user_id):
        if user_id is None or user_id == 'me':
            if not self.request.user:
                raise NotFound(detail="사용자를 찾을 수 없습니다.")
            return self.request.user

        return get_object_or_404(User, id=user_id)

class CurrentScheduleAndUserMixin(CurrentScheduleMixin, CurrentUserMixin):
    def get_schedule_and_user(self, schedule_id, user_id):
        schedule = self.get_schedule(schedule_id)
        user = self.get_user(user_id)
        return schedule, user
