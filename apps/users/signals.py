from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.users.models import Group

@receiver(post_save, sender=Group)
def update_user_global_limit(sender, instance, created, **kwargs):
    pass
