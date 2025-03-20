from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    # Skip if this is a raw save (e.g., during migrations)
    if kwargs.get('raw', False):
        return

    # Use transaction.atomic to ensure atomicity
    with transaction.atomic():
        try:
            # Try to get existing profile
            profile = Profile.objects.get(user=instance)
        except Profile.DoesNotExist:
            # Create new profile if it doesn't exist
            Profile.objects.create(
                user=instance,
                name=instance.get_full_name() or instance.username
            )

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    # Skip if this is a raw save (e.g., during migrations)
    if kwargs.get('raw', False):
        return

    try:
        profile = instance.profile
        profile.name = instance.get_full_name() or instance.username
        profile.save()
    except Profile.DoesNotExist:
        # If profile doesn't exist, create it
        Profile.objects.create(
            user=instance,
            name=instance.get_full_name() or instance.username
        )
