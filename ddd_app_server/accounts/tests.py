from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient

class AccountsViewsTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword', email='test@example.com')

    def test_check_email_used_view_email_used(self):
        """
        Test the CheckEmailUsedView with an email that is already in use.
        """
        url = reverse('check_email_used')
        data = {'email': 'test@example.com'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['data']['email_used'])

    def test_check_email_used_view_email_not_used(self):
        """
        Test the CheckEmailUsedView with an email that is not in use.
        """
        url = reverse('check_email_used')
        data = {'email': 'new@example.com'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data['data']['email_used'])

    def test_profile_view(self):
        """
        Test the ProfileView with an authenticated user.
        """
        self.client.login(username='testuser', password='testpassword')
        url = reverse('account_profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/profile.html')
        self.assertIn('access_token', response.context)
        self.assertIn('refresh_token', response.context)

    def test_email_token_obtain_pair_view(self):
        """
        Test the EmailTokenObtainPairView with valid credentials.
        """
        url = reverse('token_obtain_email')
        data = {'email': 'test@example.com', 'password': 'testpassword'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data['data'])
        self.assertIn('refresh', response.data['data'])