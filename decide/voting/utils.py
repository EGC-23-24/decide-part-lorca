from django.utils import timezone
from .models import Voting
from decide.celery import app
from .tasks import future_stop_voting_task


def future_stop_task_manager(voting_id):
    """
    Manages the scheduling and revocation of a future stop task for a voting event.

    This function checks if a voting event has a scheduled end date and manages the
    Celery task associated with stopping the voting at the specified future date and time.
    If an existing task is found for the voting event, it is revoked and a new task is
    scheduled if a future stop date is set.

    Args:
        voting_id (int): The primary key of the voting event to be managed.

    Returns:
        None: This function does not return anything but manages the scheduling and
        revocation of Celery tasks based on the voting event's schedule.
    """

    voting = Voting.objects.get(pk=voting_id)

    if not voting.end_date:

        future_stop = voting.future_stop

        task = app.tasks.get(
            f'future_stop_voting_task-{voting_id}-{voting.created_at}')
        if task:
            app.control.revoke(
                f'future_stop_voting_task-{voting_id}-{voting.created_at}', terminate=True)

        if future_stop:
            future_stop_voting_task.apply_async(
                args=[voting_id, voting.created_at], eta=future_stop, task_id=f'future_stop_voting_task-{voting_id}-{voting.created_at}')
