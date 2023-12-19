from celery import shared_task
from django.utils import timezone
from .models import Voting
from decide.celery import app


@shared_task()
def future_stop_voting_task(voting_id, created_at):
    """
    A Celery task to automatically stop a voting process at a scheduled future time.

    This function sets the end date of a voting event to its pre-configured future stop time
    and saves the changes to the database. It also ensures the revocation of the current task
    to prevent any redundant execution in the future.

    Args:
        voting_id (int): The unique identifier of the voting event to be stopped.
        created_at (datetime): The timestamp of when the voting event was created.

    Returns:
        None: This function performs an action (updating the voting event and revoking the task)
        but does not return any value.
    """

    voting = Voting.objects.get(id=voting_id)

    voting.end_date = voting.future_stop
    voting.save()
    app.control.revoke(
        f'future_stop_voting_task-{voting_id}-{created_at}',
        terminate=True)
