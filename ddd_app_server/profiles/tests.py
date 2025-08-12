from django.test import TestCase
from django.contrib.auth.models import User
from .models import Profile

class ProfileModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')

    def test_profile_creation(self):
        """
        Test that a Profile object is created automatically when a User is created.
        """
        self.assertTrue(Profile.objects.filter(user=self.user).exists())

    def test_profile_str_representation(self):
        """
        Test the string representation of the Profile model.
        """
        profile = Profile.objects.get(user=self.user)
        self.assertEqual(str(profile), self.user.username)

    def test_profile_deletion_prevention(self):
        """
        Test that a Profile object cannot be deleted.
        """
        profile = Profile.objects.get(user=self.user)
        with self.assertRaises(PermissionError):
            profile.delete()
