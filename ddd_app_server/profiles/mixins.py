from django.shortcuts import get_object_or_404
from .models import Profile

class MyProfileMixin:
    def get_profile(self, profile_id):
        if profile_id == 'me':
            return self.request.user.profile
        return get_object_or_404(Profile, id=profile_id)