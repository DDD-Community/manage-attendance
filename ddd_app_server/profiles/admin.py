from django.contrib import admin
from .models import Profile
from django.contrib.auth.models import Group
import random

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'name', 'email', 'created_at', 'updated_at')
    search_fields = ('user__username', 'user__email', 'user__groups__name')

    @admin.display(description='User ID')
    def user_id(self, obj):
        return obj.user.id

    @admin.display(description='Email')
    def email(self, obj):
        return obj.user.email

admin.site.register(Profile, ProfileAdmin)
