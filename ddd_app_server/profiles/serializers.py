from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from profiles.models import Profile, Cohort
from invites.models import InviteCode
from django.utils import timezone

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class ProfileSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    invite_code_id = serializers.UUIDField(required=False, allow_null=True)
    role = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    team = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    crew = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    responsibility = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    cohort = serializers.PrimaryKeyRelatedField(queryset=Cohort.objects.all(), allow_null=True, required=False)
    name = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    is_staff = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ['id', 'user_id', 'name', 'invite_code_id', 'role', 'team', 'crew', 'responsibility', 'cohort', 'is_staff', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user_id', 'created_at', 'is_staff', 'updated_at']

    def get_is_staff(self, obj):
        return obj.user.is_staff or obj.user.groups.filter(name="moderator").exists()

    def to_representation(self, instance):
        """Customize the serialized output."""
        representation = super().to_representation(instance)
        representation['invite_code_id'] = instance.invite_code.id if instance.invite_code else None
        return representation

    def update(self, instance, validated_data):
        """Update the profile fields."""
        request_user = self.context['request'].user

        instance.name = validated_data.get('name', instance.name)
        instance.role = validated_data.get('role', instance.role)
        instance.team = validated_data.get('team', instance.team)
        instance.crew = validated_data.get('crew', instance.crew)
        instance.responsibility = validated_data.get('responsibility', instance.responsibility)
        instance.cohort = validated_data.get('cohort', instance.cohort)

        if 'invite_code_id' in validated_data:
            self._handle_invite_code(instance, validated_data['invite_code_id'], request_user)

        instance.save()
        return instance

    def _handle_invite_code(self, instance, invite_code_id, request_user):
        """Validate and associate an invite code with the profile."""
        try:
            invite_code = InviteCode.objects.get(id=invite_code_id)
            if invite_code.used and invite_code.one_time_use:
                raise serializers.ValidationError({"invite_code_id": "This invite code has already been used."})
            if invite_code.expire_time < timezone.now():
                raise serializers.ValidationError({"invite_code_id": "This invite code has expired."})

            instance.invite_code = invite_code
            if invite_code.one_time_use:
                invite_code.used = True
                invite_code.save()

            # Add the user to the invite type group
            type_group, _ = Group.objects.get_or_create(name=invite_code.invite_type)
            request_user.groups.add(type_group)
        except InviteCode.DoesNotExist:
            raise serializers.ValidationError({"invite_code_id": "Invalid invite code."})

class ProfileSummarySerializer(ProfileSerializer):
    class Meta:
        model = Profile
        fields = ['id', 'user_id', 'name', 'role', 'team', 'cohort']
        read_only_fields = fields

