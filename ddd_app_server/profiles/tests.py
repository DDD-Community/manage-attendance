from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from profiles.models import Profile

User = get_user_model()


class ProfileCreationTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_create_profile_creates_user_and_profile(self):
        data = {
            "email": "newuser@example.com",
            "password": "pass1234",
            "name": "New User",
        }
        url = reverse("profile-create")
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertTrue(User.objects.filter(email="newuser@example.com").exists())
        self.assertTrue(
            Profile.objects.filter(user__email="newuser@example.com").exists()
        )
