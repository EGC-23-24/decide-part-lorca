from celery import shared_task
from django.utils import timezone
from .models import Voting
from decide.celery import app

@shared_task()
def future_stop_voting_task(voting_id, created_at):
    voting = Voting.objects.get(id=voting_id)
    
    voting.end_date = voting.future_stop
    voting.save()
    app.control.revoke(f'future_stop_voting_task-{voting_id}-{created_at}', terminate=True)
        