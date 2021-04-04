from django.dispatch.dispatcher import receiver
from django.db.models.signals import post_save
from .models import CustomUser
from .models import Profile

@receiver(post_save, sender=CustomUser)
def save_profile(sender, instance, created, **kwarg):
    if created:
        Profile.objects.create(user=instance, name=instance.username)


