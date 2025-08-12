from django.test import TestCase
from django.contrib.auth.models import Group
from .models import Schedule
from django.utils import timezone

class ScheduleModelTest(TestCase):

    def setUp(self):
        self.group = Group.objects.create(name='Test Group')

    def test_schedule_creation_defaults(self):
        """
        Test that a Schedule object can be created with default values.
        """
        schedule = Schedule.objects.create(
            title='Test Schedule',
            start_time=timezone.now(),
            end_time=timezone.now() + timezone.timedelta(hours=1)
        )
        self.assertIsInstance(schedule, Schedule)
        self.assertEqual(Schedule.objects.count(), 1)
        self.assertIsNone(schedule.group)

    def test_schedule_creation_custom(self):
        """
        Test that a Schedule object can be created with custom values.
        """
        schedule = Schedule.objects.create(
            title='Test Schedule',
            description='Test description',
            start_time=timezone.now(),
            end_time=timezone.now() + timezone.timedelta(hours=1),
            group=self.group,
        )
        self.assertIsInstance(schedule, Schedule)
        self.assertEqual(Schedule.objects.count(), 1)
        self.assertEqual(schedule.group, self.group)

    def test_schedule_str_representation(self):
        """
        Test the string representation of the Schedule model.
        """
        start_time = timezone.now()
        schedule = Schedule.objects.create(
            title='Test Schedule',
            start_time=start_time,
            end_time=start_time + timezone.timedelta(hours=1)
        )
        self.assertEqual(str(schedule), f"{schedule.title} ({start_time.strftime('%Y-%m-%d %H:%M')})")