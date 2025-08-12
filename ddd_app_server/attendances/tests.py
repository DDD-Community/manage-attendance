from django.test import TestCase
from django.contrib.auth.models import User
from .models import Attendance
from schedules.models import Schedule
from django.utils import timezone

class AttendanceModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.schedule = Schedule.objects.create(
            title='Test Schedule',
            start_time=timezone.now(),
            end_time=timezone.now() + timezone.timedelta(hours=1)
        )

    def test_attendance_creation_defaults(self):
        """
        Test that an Attendance object can be created with default values.
        """
        attendance = Attendance.objects.create(user=self.user, schedule=self.schedule)
        self.assertIsInstance(attendance, Attendance)
        self.assertEqual(Attendance.objects.count(), 1)
        self.assertEqual(attendance.status, 'tbd')
        self.assertIsNone(attendance.method)
        self.assertIsNone(attendance.note)

    def test_attendance_creation_custom(self):
        """
        Test that an Attendance object can be created with custom values.
        """
        attendance = Attendance.objects.create(
            user=self.user,
            schedule=self.schedule,
            status='present',
            method='qr',
            note='Test note'
        )
        self.assertIsInstance(attendance, Attendance)
        self.assertEqual(Attendance.objects.count(), 1)
        self.assertEqual(attendance.status, 'present')
        self.assertEqual(attendance.method, 'qr')
        self.assertEqual(attendance.note, 'Test note')

    def test_attendance_str_representation(self):
        """
        Test the string representation of the Attendance model.
        """
        attendance = Attendance.objects.create(user=self.user, schedule=self.schedule)
        self.assertEqual(str(attendance), f"{self.user} - {self.schedule} ({attendance.status})")