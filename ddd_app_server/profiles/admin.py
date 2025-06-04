from django.contrib import admin
from .models import Profile

class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user_id', 'user', 'email', 'name', 'role', 'team', 'crew',
        'responsibility', 'cohort', 'created_at'
    )
    search_fields = (
        'user__username', 'user__email', 'role', 'team', 'crew', 'responsibility', 'cohort__name'
    )

    @admin.display(description='User ID')
    def user_id(self, obj):
        return obj.user.id

    @admin.display(description='Email')
    def email(self, obj):
        return obj.user.email

admin.site.register(Profile, ProfileAdmin)
