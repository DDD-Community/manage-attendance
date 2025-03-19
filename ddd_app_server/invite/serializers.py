from rest_framework import serializers
from .models import InviteCode
from django.utils.timezone import now
import random
import string

class InviteCodeSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source='created_by.username')
    
    class Meta:
        model = InviteCode
        fields = ['id', 'code', 'invite_type', 'used', 'expire_time', 'one_time_use', 'created_at', 'created_by']
        read_only_fields = ['id', 'code', 'used', 'created_at', 'created_by']

    def generate_code(self):
        while True:
            code = ''.join(random.choices(string.digits, k=4))
            if not InviteCode.objects.filter(code=code, expire_time__gte=now(), used=False).exists():
                return code

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        validated_data['code'] = self.generate_code()
        return super().create(validated_data)
