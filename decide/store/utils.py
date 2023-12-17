from django.utils import timezone
from django.utils.dateparse import parse_datetime
from rest_framework import status
from rest_framework.response import Response

from .models import Vote
from base import mods

def classic_store(request):
  """
    * voting: id
    * voter: id
    * vote: { "a": int, "b": int }
    * voting_type: "yesno" || "classic" || "comment" || "preference"

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
    * voting: id
    * voter: id
    * votes: list<{ "a": int, "b": int }>
    * voting_type: "choices"
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