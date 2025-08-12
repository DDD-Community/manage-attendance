from django.test import TestCase
from django.contrib.auth.models import User
from .models import QRLog

class QRLogModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')

    def test_qr_log_creation(self):
        """
        Test that a QRLog object can be created.
        """
        qr_log = QRLog.objects.create(user=self.user)
        self.assertIsInstance(qr_log, QRLog)
        self.assertEqual(QRLog.objects.count(), 1)

    def test_qr_log_str_representation(self):
        """
        Test the string representation of the QRLog model.
        """
        qr_log = QRLog.objects.create(user=self.user)
        self.assertEqual(str(qr_log), f"QRLog for {self.user.username} at {qr_log.created_at}")