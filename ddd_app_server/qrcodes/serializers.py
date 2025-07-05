from rest_framework import serializers
from .models import QRLog

class QRLogSerializer(serializers.ModelSerializer):
    qr_string = serializers.ReadOnlyField(source='id')

    class Meta:
        model = QRLog
        fields = ['id', 'user', 'qr_string', 'created_at', 'expires_at', 'decoded_at']
        read_only_fields = ['id', 'user', 'qr_string', 'created_at', 'decoded_at']
