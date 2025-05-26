from rest_framework import serializers
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from profiles.models import Profile
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
    role = serializers.CharField(required=False, allow_null=True)
    team = serializers.CharField(required=False, allow_null=True)
    crew = serializers.CharField(required=False, allow_null=True)
    responsibility = serializers.CharField(required=False, allow_null=True)
    cohort = serializers.CharField(required=False, allow_null=True)
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
        user_groups = instance.user.groups.all()

        # Extract group-based fields
        representation['role'] = self._extract_group_value(user_groups, "role:")
        representation['team'] = self._extract_group_value(user_groups, "team:")
        representation['crew'] = self._extract_group_value(user_groups, "team:")  # TODO: Keep crew for now
        representation['responsibility'] = self._extract_group_value(user_groups, "responsibility:")
        representation['cohort'] = self._extract_group_value(user_groups, "cohort:")

        # Include invite_code_id if available
        if 'invite_code_id' in representation:
            representation['invite_code_id'] = instance.invite_code.id if instance.invite_code else None

        return representation

    def update(self, instance, validated_data):
        """Update the profile and manage related groups."""
        request_user = self.context['request'].user

        # Update basic fields
        self._update_field(instance, validated_data, 'name')

        # Handle invite code
        if 'invite_code_id' in validated_data:
            self._handle_invite_code(instance, validated_data['invite_code_id'], request_user)

        # Update group-based fields
        self._update_group(request_user, validated_data, 'role', "role:")
        self._update_group(request_user, validated_data, 'team', "team:")
        self._update_group(request_user, validated_data, 'crew', "team:")  # TODO: Keep crew for now
        self._update_group(request_user, validated_data, 'responsibility', "responsibility:")
        self._update_group(request_user, validated_data, 'cohort', "cohort:")

        instance.save()
        return instance

    def _extract_group_value(self, user_groups, prefix):
        """Extract the value of a group based on its prefix."""
        group = next((g for g in user_groups if g.name.startswith(prefix)), None)
        return group.name.split(":", 1)[1] if group else ""

    def _update_field(self, instance, validated_data, field_name):
        """Update a field on the instance if provided in validated_data."""
        if field_name in validated_data and validated_data[field_name]:
            setattr(instance, field_name, validated_data[field_name])

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

    def _update_group(self, user, validated_data, field_name, prefix):
        """Update a user's group membership for a specific field."""
        if field_name in validated_data and validated_data[field_name]:
            # Remove existing groups with the same prefix
            groups = user.groups.filter(name__startswith=prefix)
            user.groups.remove(*groups)

            # Add the new group
            group_name = f"{prefix}{validated_data[field_name]}"
            group, _ = Group.objects.get_or_create(name=group_name)
            user.groups.add(group)


class ProfileSummarySerializer(ProfileSerializer):
    class Meta:
        model = Profile
        fields = ['id', 'user_id', 'name', 'role', 'team', 'cohort']
        read_only_fields = fields

