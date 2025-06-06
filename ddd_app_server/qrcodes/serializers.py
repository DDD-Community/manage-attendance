from rest_framework import serializers
from .models import QRLog

class QRLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = QRLog
        fields = ['id', 'user', 'created_at', 'expires_at', 'decoded_at']
        read_only_fields = ['id', 'user', 'created_at', 'decoded_at']
