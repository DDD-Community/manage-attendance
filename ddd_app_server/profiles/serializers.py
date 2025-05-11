from rest_framework import serializers
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from schedules.models import Attendance
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
    invite_code_id = serializers.UUIDField(required=False, allow_null=True)
    role = serializers.CharField(required=False, allow_null=True)
    team = serializers.CharField(required=False, allow_null=True)
    cohort = serializers.CharField(required=False, allow_null=True)
    is_staff = serializers.SerializerMethodField()
    attendance = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ['id', 'name', 'invite_code_id', 'role', 'team', 'cohort', 'is_staff', 'created_at', 'updated_at', 'attendance']
        read_only_fields = ['id', 'created_at', 'is_staff', 'updated_at']

    def get_is_staff(self, obj):
        return obj.user.is_staff or obj.user.groups.filter(name="moderator").exists()
    
    def get_attendance(self, obj):
        attendances = Attendance.objects.filter(user=obj.user)
        if attendances.exists():
            attendance_count = attendances.count()
            
            late_count = attendances.filter(status="late").count()
            absent_count = attendances.filter(status="absent").count()
            present_count = attendances.filter(status="present").count()
            exception_count = attendances.filter(status="exception").count()
            tbd_count = attendances.filter(status="tbd").count()
            
            return {
                "attendance_count": attendance_count,
                "late_count": late_count,
                "absent_count": absent_count,
                "present_count": present_count,
                "exception_count": exception_count,
                "tbd_count": tbd_count,
            }
        return {
            "attendance_count": 0,
            "late_count": 0,
            "absent_count": 0,
            "present_count": 0,
            "exception_count": 0,
            "tbd_count": 0,
        }

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        user_groups = instance.user.groups.all()
        
        # Extract role from groups
        role_group = next((g for g in user_groups if g.name.startswith("role:")), None)
        representation['role'] = role_group.name.split(":", 1)[1] if role_group else None
        
        # Extract team from groups
        team_group = next((g for g in user_groups if g.name.startswith("team:")), None)
        representation['team'] = team_group.name.split(":", 1)[1] if team_group else None
        
        # Extract cohort from groups
        cohort_group = next((g for g in user_groups if g.name.startswith("cohort:")), None)
        representation['cohort'] = cohort_group.name.split(":", 1)[1] if cohort_group else None
        
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

        # Update cohort group
        if 'cohort' in validated_data:
            request_user.groups.filter(name__startswith="cohort:").delete()
            if validated_data['cohort']:
                cohort_group, _ = Group.objects.get_or_create(name=f"cohort:{validated_data['cohort']}")
                request_user.groups.add(cohort_group)
        
        instance.save()
        return instance
