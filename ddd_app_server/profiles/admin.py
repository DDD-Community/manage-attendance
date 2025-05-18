from django.contrib import admin
from .models import Profile, Cohort
from django.contrib.auth.models import Group
import random

@admin.action(description='Assign "cohort:12" to selected profiles')
def assign_cohort_12(modeladmin, request, queryset):
    cohort_group, created = Group.objects.get_or_create(name="cohort:12")
    for profile in queryset:
        profile.user.groups.add(cohort_group)

@admin.action(description='Assign a random group to selected profiles')
def assign_random_group(modeladmin, request, queryset):
    role_gropus = Group.objects.filter(name__startswith="role:")
    team_groups = Group.objects.filter(name__startswith="team:")
    responsibility_groups = Group.objects.filter(name__startswith="responsibility:")
    cohort_groups = Group.objects.filter(name__startswith="cohort:")
    for profile in queryset:
        random_role_group, _ = Group.objects.get_or_create(name=random.choice(role_gropus).name)
        random_team_group, _ = Group.objects.get_or_create(name=random.choice(team_groups).name)
        random_responsibility_group, _ = Group.objects.get_or_create(name=random.choice(responsibility_groups).name)
        random_cohort_group, _ = Group.objects.get_or_create(name=random.choice(cohort_groups).name)
        profile.user.groups.add(random_role_group)
        profile.user.groups.add(random_team_group)
        profile.user.groups.add(random_responsibility_group)
        profile.user.groups.add(random_cohort_group)

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'name', 'created_at')
    search_fields = ('user__username', 'user__group__name')
    actions = [assign_cohort_12, assign_random_group]

class CohortAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'created_at')
    search_fields = ('name',)

admin.site.register(Profile, ProfileAdmin)
admin.site.register(Cohort, CohortAdmin)