from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile

@receiver(post_save, sender=User)
def update_profile(sender, instance, created, **kwargs):
    """
    Create or update the user profile when a User instance is created or updated.
    """
    Profile.objects.update_or_create(
        user=instance,
        defaults={'name': instance.get_full_name() or instance.username}
    )
