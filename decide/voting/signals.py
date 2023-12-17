from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from .models import Voting
from .utils import future_stop_task_manager


@receiver(post_save, sender=Voting)
def future_stop_add_task(sender, created, instance, **kwargs):
    instance.created_at = timezone.now()
    future_stop_task_manager(instance.id)