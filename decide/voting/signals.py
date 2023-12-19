from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from .models import Voting
from .utils import future_stop_task_manager


@receiver(post_save, sender=Voting)
def future_stop_add_task(sender, created, instance, **kwargs):
    """
    A Django signal receiver that triggers a task manager for future stop voting events.

    This function is called automatically after a Voting object is saved. It sets the
    'created_at' attribute of the Voting instance to the current time and then calls the
    future stop task manager with the instance's ID.

    Args:
        sender (Model): The model class that sent the signal.
        created (bool): True if a new record was created.
        instance (Voting): The instance of the Voting model that was saved.
        **kwargs: Additional keyword arguments.

    Returns:
        None: This function does not return a value, but triggers the future_stop_task_manager function.
    """
    instance.created_at = timezone.now()
    future_stop_task_manager(instance.id)
