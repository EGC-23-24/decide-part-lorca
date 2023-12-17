from django.utils import timezone
from django.utils.dateparse import parse_datetime
from rest_framework import status
from rest_framework.response import Response

from .models import Vote
from base import mods

def classic_store(request):
    """
    Processes and stores a classic type vote.

    Args:
        request: Django HttpRequest object containing vote data.
    
    The request should contain:
        - voting (int): The ID of the voting.
        - voter (int): The ID of the voter.
        - vote (dict): A dictionary containing the 'a' and 'b' keys representing the encrypted vote.
        - voting_type (str): A string representing the type of voting ('yesno', 'classic', 'comment', 'preference').

    Returns:
        HTTP status code indicating the result of the operation.

    Raises:
        HTTP_401_UNAUTHORIZED: If the voting is not found, or has not started, or is closed.
        HTTP_400_BAD_REQUEST: If the voting ID, voter ID, or vote data is missing or invalid.
    """
  
    vid = request.data.get('voting')
    voting = mods.get('voting', params={'id': vid})
    if not voting or not isinstance(voting, list):
        return status.HTTP_401_UNAUTHORIZED
    start_date = voting[0].get('start_date', None)
    end_date = voting[0].get('end_date', None)
    not_started = not start_date or timezone.now() < parse_datetime(start_date)
    is_closed = end_date and parse_datetime(end_date) < timezone.now()
    if not_started or is_closed:
        return status.HTTP_401_UNAUTHORIZED

    uid = request.data.get('voter')
    vote = request.data.get('vote')

    if not vid or not uid or not vote:
        return status.HTTP_400_BAD_REQUEST

    # validating voter
    if request.auth:
        token = request.auth.key
    else:
        token = "NO-AUTH-VOTE"
    voter = mods.post('authentication', entry_point='/getuser/', json={'token': token})
    voter_id = voter.get('id', None)
    if not voter_id or voter_id != uid:
        return status.HTTP_401_UNAUTHORIZED

    # the user is in the census
    perms = mods.get('census/{}'.format(vid), params={'voter_id': uid}, response=True)
    if perms.status_code == 401:
        return status.HTTP_401_UNAUTHORIZED

    a = vote.get("a")
    b = vote.get("b")

    defs = { "a": a, "b": b }
    v, _ = Vote.objects.get_or_create(voting_id=vid, voter_id=uid,
                                        defaults=defs)
    v.a = a
    v.b = b

    v.save()
    
    return status.HTTP_200_OK

def choices_store(request):
    """
    Processes and stores votes for a voting of type 'choices'.

    Args:
        request: Django HttpRequest object containing votes data.

    The request should contain:
        - voting (int): The ID of the voting.
        - voter (int): The ID of the voter.
        - votes (list): A list of dictionaries, each containing the 'a' and 'b' keys representing individual encrypted votes.
        - voting_type (str): A string representing the type of voting ('choices').

    Returns:
        HTTP status code indicating the result of the operation.

    Raises:
        HTTP_401_UNAUTHORIZED: If the voting is not found, or has not started, or is closed.
        HTTP_400_BAD_REQUEST: If the voting ID, voter ID, or votes data is missing or invalid.
    """

    vid = request.data.get('voting')
    voting = mods.get('voting', params={'id': vid})
    if not voting or not isinstance(voting, list):
        return status.HTTP_401_UNAUTHORIZED
    start_date = voting[0].get('start_date', None)
    end_date = voting[0].get('end_date', None)
    not_started = not start_date or timezone.now() < parse_datetime(start_date)
    is_closed = end_date and parse_datetime(end_date) < timezone.now()
    if not_started or is_closed:
        return status.HTTP_401_UNAUTHORIZED

    uid = request.data.get('voter')
    votes = request.data.get('votes')

    if not vid or not uid or not votes:
        return status.HTTP_400_BAD_REQUEST

    # validating voter
    if request.auth:
        token = request.auth.key
    else:
        token = "NO-AUTH-VOTE"
    voter = mods.post('authentication', entry_point='/getuser/', json={'token': token})
    voter_id = voter.get('id', None)
    if not voter_id or voter_id != uid:
        return status.HTTP_401_UNAUTHORIZED

    # the user is in the census
    perms = mods.get('census/{}'.format(vid), params={'voter_id': uid}, response=True)
    if perms.status_code == 401:
        return status.HTTP_401_UNAUTHORIZED

    vote = Vote.objects.filter(voter_id=uid, voting_id=vid).first()

    if vote != None:
        Vote.objects.filter(voter_id=uid, voting_id=vid).delete()  
            
    for v in votes:
        a = v.get("a")
        b = v.get("b")

        defs = { "a": a, "b": b }
        voteDB, _ = Vote.objects.get_or_create(voting_id=vid, voter_id=uid, a=a, b=b, defaults=defs)
        voteDB.a = a
        voteDB.b = b

        voteDB.save()

    return status.HTTP_200_OK