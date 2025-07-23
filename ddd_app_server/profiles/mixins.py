from django.shortcuts import get_object_or_404
from .models import Profile
from django.http import Http404

class CurrentProfileMixin:
    def get_profile(self, profile_id):
        if profile_id is None or profile_id == 'me':
            if hasattr(self.request.user, 'profile'):
                return self.request.user.profile
            else:
                raise Http404("Profile does not exist for the current user.")
        return get_object_or_404(Profile, id=profile_id)
