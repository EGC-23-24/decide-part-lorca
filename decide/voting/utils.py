from django.utils import timezone
from .models import Voting
from decide.celery import app
from .tasks import future_stop_voting_task


def future_stop_task_manager(voting_id):
    voting = Voting.objects.get(pk=voting_id)
    
    if not voting.end_date:
    
        future_stop = voting.future_stop
        
        task = app.tasks.get(f'future_stop_voting_task-{voting_id}-{voting.created_at}')
        if task:
            app.control.revoke(f'future_stop_voting_task-{voting_id}-{voting.created_at}', terminate=True)


        if future_stop:
            future_stop_voting_task.apply_async(args=[voting_id, voting.created_at], eta=future_stop, task_id=f'future_stop_voting_task-{voting_id}-{voting.created_at}')