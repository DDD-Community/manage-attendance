from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from .models import InviteCode, one_week_from_now

class InviteCodeModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')

    def test_one_week_from_now(self):
        """
        Test the one_week_from_now function.
        """
        now = timezone.now()
        one_week_later = one_week_from_now()
        self.assertAlmostEqual(one_week_later, now + timedelta(days=7), delta=timedelta(seconds=1))

    def test_invite_code_creation_defaults(self):
        """
        Test that an InviteCode object can be created with default values.
        """
        invite_code = InviteCode.objects.create(code='DEFAULT', invite_type='member', created_by=self.user)
        self.assertIsInstance(invite_code, InviteCode)
        self.assertEqual(InviteCode.objects.count(), 1)
        self.assertFalse(invite_code.used)
        self.assertTrue(invite_code.one_time_use)
        self.assertAlmostEqual(invite_code.expire_time, timezone.now() + timedelta(days=7), delta=timedelta(seconds=1))

    def test_invite_code_creation_custom(self):
        """
        Test that an InviteCode object can be created with custom values.
        """
        expire_time = timezone.now() + timedelta(days=30)
        invite_code = InviteCode.objects.create(
            code='CUSTOM',
            invite_type='moderator',
            created_by=self.user,
            used=True,
            one_time_use=False,
            expire_time=expire_time
        )
        self.assertIsInstance(invite_code, InviteCode)
        self.assertEqual(InviteCode.objects.count(), 1)
        self.assertTrue(invite_code.used)
        self.assertFalse(invite_code.one_time_use)
        self.assertEqual(invite_code.expire_time, expire_time)

    def test_invite_code_str_representation(self):
        """
        Test the string representation of the InviteCode model.
        """
        invite_code = InviteCode.objects.create(code='STRTEST', invite_type='member', created_by=self.user)
        self.assertEqual(str(invite_code), 'STRTEST')