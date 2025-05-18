from rest_framework import serializers
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
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
    role = serializers.CharField(required=False, allow_null=True)
    team = serializers.CharField(required=False, allow_null=True)
    crew = serializers.CharField(required=False, allow_null=True)
    responsibility = serializers.CharField(required=False, allow_null=True)  # changed from moderator_role
    cohort = serializers.CharField(required=False, allow_null=True)
    is_staff = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ['id', 'user_id', 'name', 'invite_code_id', 'role', 'team', 'crew', 'responsibility', 'cohort', 'cohort_id', 'is_staff', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user_id', 'created_at', 'is_staff', 'updated_at']

    def get_is_staff(self, obj):
        return obj.user.is_staff or obj.user.groups.filter(name="moderator").exists()
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        user_groups = instance.user.groups.all()
        
        # Extract role from groups
        role_group = next((g for g in user_groups if g.name.startswith("role:")), None)
        representation['role'] = role_group.name.split(":", 1)[1] if role_group else None
        
        # Extract team from groups
        team_group = next((g for g in user_groups if g.name.startswith("team:")), None)
        representation['team'] = team_group.name.split(":", 1)[1] if team_group else None
        
        # Extract crew from groups
        # TODO i've replaced crew with team in the serializer, but we need to keep the crew group for now
        crew_group = next((g for g in user_groups if g.name.startswith("team:")), None)
        representation['crew'] = crew_group.name.split(":", 1)[1] if crew_group else None

        # Extract responsibility from groups (was moderator_role)
        responsibility_group = next((g for g in user_groups if g.name.startswith("responsibility:")), None)
        representation['responsibility'] = responsibility_group.name.split(":", 1)[1] if responsibility_group else None
        
        # Extract cohort from groups
        cohort = next((g for g in user_groups if g.name.startswith("cohort:")), None)
        representation['cohort'] = cohort.name.split(":", 1)[1] if cohort else None
        
        # Include invite_code_id if available
        representation['invite_code_id'] = instance.invite_code.id if instance.invite_code else None
        
        return representation

    def update(self, instance, validated_data):
        request_user = self.context['request'].user
        
        # Update name if provided
        if 'name' in validated_data:
            instance.name = validated_data['name']
        
        # Update invite code if provided
        if 'invite_code_id' in validated_data:
            try:
                invite_code = InviteCode.objects.get(id=validated_data['invite_code_id'])
                if invite_code.used and invite_code.one_time_use:
                    raise serializers.ValidationError({"invite_code_id": "This invite code has already been used."})
                if invite_code.expire_time < timezone.now():
                    raise serializers.ValidationError({"invite_code_id": "This invite code has expired."})
                instance.invite_code = invite_code
                if invite_code.one_time_use:
                    invite_code.used = True
                    invite_code.save()
                # Update type group
                type_group, _ = Group.objects.get_or_create(name=invite_code.invite_type)
                request_user.groups.add(type_group)
            except InviteCode.DoesNotExist:
                raise serializers.ValidationError({"invite_code_id": "Invalid invite code."})
        
        # Update role group
        if 'role' in validated_data:
            request_user.groups.filter(name__startswith="role:").delete()
            if validated_data['role']:
                role_group, _ = Group.objects.get_or_create(name=f"role:{validated_data['role']}")
                request_user.groups.add(role_group)
        
        # Update team group
        if 'team' in validated_data:
            request_user.groups.filter(name__startswith="team:").delete()
            if validated_data['team']:
                team_group, _ = Group.objects.get_or_create(name=f"team:{validated_data['team']}")
                request_user.groups.add(team_group)

        # Update crew group
        # TODO i've replaced crew with team in the serializer, but we need to keep the crew group for now
        if 'crew' in validated_data:
            request_user.groups.filter(name__startswith="team:").delete()
            if validated_data['crew']:
                crew_group, _ = Group.objects.get_or_create(name=f"team:{validated_data['crew']}")
                request_user.groups.add(crew_group)

        # Update responsibility group (was moderator_role)
        if 'responsibility' in validated_data:
            request_user.groups.filter(name__startswith="responsibility:").delete()
            if validated_data['responsibility']:
                responsibility_group, _ = Group.objects.get_or_create(name=f"responsibility:{validated_data['responsibility']}")
                request_user.groups.add(responsibility_group)

        # Update cohort group
        # TODO remove cohort group from groups and replace it with cohort data model
        if 'cohort' in validated_data:
            request_user.groups.filter(name__startswith="cohort:").delete()
            request_user.profile.cohort = None
            if validated_data['cohort']:
                cohort_group, _ = Group.objects.get_or_create(name=f"cohort:{validated_data['cohort']}")
                request_user.groups.add(cohort_group)
                cohort, _ = Cohort.objects.get_or_create(name=validated_data['cohort'])
                instance.cohort_id = cohort

        instance.save()
        return instance


class ProfileSummarySerializer(ProfileSerializer):
    class Meta:
        model = Profile
        fields = ['name', 'role', 'team', 'cohort']
        read_only_fields = fields

