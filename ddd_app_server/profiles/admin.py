from django.contrib import admin
from .models import Profile, Cohort
from django.contrib.auth.models import Group

@admin.action(description='Assign "cohort:12" to selected profiles')
def assign_cohort_12(modeladmin, request, queryset):
    cohort_group, created = Group.objects.get_or_create(name="cohort:12")
    for profile in queryset:
        profile.user.groups.add(cohort_group)

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'name', 'created_at')
    search_fields = ('user__username', 'user__group__name')
    actions = [assign_cohort_12]

class CohortAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'created_at')
    search_fields = ('name',)

admin.site.register(Profile, ProfileAdmin)
admin.site.register(Cohort, CohortAdmin)