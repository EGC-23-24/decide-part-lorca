import datetime
import random
from django.contrib.auth.models import User
from django.utils import timezone
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.test import APITestCase

from .models import Vote
from .serializers import VoteSerializer
from base import mods
from base.models import Auth
from base.tests import BaseTestCase
from census.models import Census
from mixnet.models import Key
from voting.models import Question, QuestionOption
from voting.models import Voting


class StoreChoiceCase(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.question = Question(desc='qwerty', type='C')
        self.question_choices = Question(desc='qwerty', type='M')
        self.question.save()
        self.question_choices.save()
        
        self.voting = Voting(pk=5001,
                             name='voting example',
                             question=self.question,
                             start_date=timezone.now(),
        )
        self.voting_choices = Voting(pk=5002,
                             name='voting example text',
                             question=self.question_choices,
                             start_date=timezone.now(),)
        self.voting.save()
        self.voting_choices.save()

    def tearDown(self):
        self.question = None
        self.question_choices = None
        self.voting = None
        self.voting_choices = None
        
        super().tearDown()

    def gen_voting(self, pk):
        voting = Voting(pk=pk, name='v1', desc="v1 desc", question=self.question, start_date=timezone.now(),
                end_date=timezone.now() + datetime.timedelta(days=1))
        voting.save()

    def get_or_create_user(self, pk):
        user, _ = User.objects.get_or_create(pk=pk)
        user.username = 'user{}'.format(pk)
        user.set_password('qwerty')
        user.save()
        return user

    def gen_votes(self):
        votings = [random.randint(1, 5000) for i in range(10)]
        users = [random.randint(3, 5002) for i in range(50)]
        for v in votings:
            a = random.randint(2, 500)
            b = random.randint(2, 500)
            self.gen_voting(v)
            random_user = random.choice(users)
            user = self.get_or_create_user(random_user)
            self.login(user=user.username)
            census = Census(voting_id=v, voter_id=random_user)
            census.save()
            data = {
                "voting": v,
                "voter": random_user,
                "vote": { "a": a, "b": b },
                "voting_type": 'classic',
            }
            response = self.client.post('/store/', data, format='json')
            self.assertEqual(response.status_code, 200)

        self.logout()
        return votings, users

    def test_gen_vote_invalid(self):
        data = {
            "voting": 1,
            "voter": 1,
            "vote": { "a": 1, "b": 1 },
            "voting_type": 'classic',
        }
        response = self.client.post('/store/', data, format='json')
        self.assertEqual(response.status_code, 401)

    def test_store_vote(self):
        VOTING_PK = 345
        CTE_A = 96
        CTE_B = 184
        voting = Voting(pk=VOTING_PK,
                             name='voting example',
                             question=self.question,
                             start_date=timezone.now(),
        )
        voting.save()
        user = self.get_or_create_user(1)
        census = Census(voting_id=VOTING_PK, voter_id=1)
        census.save()
        self.gen_voting(VOTING_PK)
        data = {
            "voting": VOTING_PK,
            "voter": 1,
            "vote": { "a": CTE_A, "b": CTE_B },
            "voting_type": 'classic',
        }
        self.login(user=user.username)
        response = self.client.post('/store/', data, format='json')
        self.assertEqual(response.status_code, 200)

        self.assertEqual(Vote.objects.count(), 1)
        self.assertEqual(Vote.objects.first().voting_id, VOTING_PK)
        self.assertEqual(Vote.objects.first().voter_id, 1)
        self.assertEqual(Vote.objects.first().a, CTE_A)
        self.assertEqual(Vote.objects.first().b, CTE_B)
    

    def test_store_vote_choices(self):
        CTE_A = 96
        CTE_B = 184
        user = self.get_or_create_user(1)
        census = Census(voting_id=self.voting_choices.id, voter_id=1)
        census.save()
        data = {
            "voting": self.voting_choices.id,
            "voter": 1,
            "votes": [{ "a": CTE_A, "b": CTE_B }, { "a": CTE_A + 1, "b": CTE_B + 1 }],
            'voting_type': 'choices'
        }
        self.login(user=user.username)
        response = self.client.post('/store/', data, format='json')
        self.assertEqual(response.status_code, 200)

        self.assertEqual(Vote.objects.count(), 2)
        self.assertEqual(Vote.objects.first().voting_id, self.voting_choices.id)
        self.assertEqual(Vote.objects.first().voter_id, 1)
        self.assertEqual(Vote.objects.filter(a=CTE_A).values()[0]['a'], CTE_A)
        self.assertEqual(Vote.objects.filter(b=CTE_B).values()[0]['b'], CTE_B)
        self.assertEqual(Vote.objects.filter(a=CTE_A + 1).values()[0]['a'], CTE_A + 1)
        self.assertEqual(Vote.objects.filter(b=CTE_B + 1).values()[0]['b'], CTE_B + 1)
    
    def test_voting_invalid_type(self):
        user = self.get_or_create_user(2)
        census = Census(voting_id=self.voting_choices.id, voter_id=2)
        census.save()
        data = {
            "voting": self.voting_choices.id,
            "voter": 1,
            "vote": { "a": 1, "b": 1 },
            'voting_type': 'invalid'
        }
        self.login(user=user.username)
        response = self.client.post('/store/', data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_store_vote_text(self):
        CTE_A = 96
        CTE_B = 184
        user = self.get_or_create_user(1)
        census = Census(voting_id=self.voting_choices.id, voter_id=1)
        census.save()
        data = {
            "voting": self.voting_choices.id,
            "voter": 1,
            "vote": { "a": CTE_A, "b": CTE_B },
            'voting_type': 'comment'
        }
        self.login(user=user.username)
        response = self.client.post('/store/', data, format='json')
        self.assertEqual(response.status_code, 200)

        self.assertEqual(Vote.objects.count(), 1)
        self.assertEqual(Vote.objects.first().voting_id, self.voting_choices.id)
        self.assertEqual(Vote.objects.first().voter_id, 1)
        self.assertEqual(Vote.objects.first().a, CTE_A)
        self.assertEqual(Vote.objects.first().b, CTE_B)
    
    def test_voting_invalid_type(self):
        user = self.get_or_create_user(2)
        census = Census(voting_id=self.voting_choices.id, voter_id=2)
        census.save()
        data = {
            "voting": self.voting_choices.id,
            "voter": 1,
            "vote": { "a": 1, "b": 1 },
            'voting_type': 'invalid'
        }

        self.login(user=user.username)
        response = self.client.post('/store/', data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_vote(self):
        self.gen_votes()
        response = self.client.get('/store/', format='json')
        self.assertEqual(response.status_code, 401)

        self.login(user='noadmin')
        response = self.client.get('/store/', format='json')
        self.assertEqual(response.status_code, 403)

        self.login()
        response = self.client.get('/store/', format='json')
        self.assertEqual(response.status_code, 200)
        votes = response.json()

        self.assertEqual(len(votes), Vote.objects.count())
        self.assertEqual(votes[0], VoteSerializer(Vote.objects.all().first()).data)
    

    def test_filter(self):
        votings, voters = self.gen_votes()
        v = votings[0]

        response = self.client.get('/store/?voting_id={}'.format(v), format='json')
        self.assertEqual(response.status_code, 401)

        self.login(user='noadmin')
        response = self.client.get('/store/?voting_id={}'.format(v), format='json')
        self.assertEqual(response.status_code, 403)

        self.login()
        response = self.client.get('/store/?voting_id={}'.format(v), format='json')
        self.assertEqual(response.status_code, 200)
        votes = response.json()

        self.assertEqual(len(votes), Vote.objects.filter(voting_id=v).count())

        v = voters[0]
        response = self.client.get('/store/?voter_id={}'.format(v), format='json')
        self.assertEqual(response.status_code, 200)
        votes = response.json()

        self.assertEqual(len(votes), Vote.objects.filter(voter_id=v).count())

    def test_hasvote(self):
        votings, voters = self.gen_votes()
        vo = Vote.objects.first()
        v = vo.voting_id
        u = vo.voter_id

        response = self.client.get('/store/?voting_id={}&voter_id={}'.format(v, u), format='json')
        self.assertEqual(response.status_code, 401)

        self.login(user='noadmin')
        response = self.client.get('/store/?voting_id={}&voter_id={}'.format(v, u), format='json')
        self.assertEqual(response.status_code, 403)

        self.login()
        response = self.client.get('/store/?voting_id={}&voter_id={}'.format(v, u), format='json')
        self.assertEqual(response.status_code, 200)
        votes = response.json()

        self.assertEqual(len(votes), 1)
        self.assertEqual(votes[0]["voting_id"], v)
        self.assertEqual(votes[0]["voter_id"], u)

    def test_voting_status(self):
        data = {
            "voting": 5001,
            "voter": 1,
            "vote": { "a": 30, "b": 55 },
            "voting_type": 'classic',
        }

        user = self.get_or_create_user(1)
        census = Census(voting_id=5001, voter_id=1)
        census.save()
        # not opened
        self.voting.start_date = timezone.now() + datetime.timedelta(days=1)
        self.voting.save()
        self.login(user=user.username)
        response = self.client.post('/store/', data, format='json')
        self.assertEqual(response.status_code, 401)

        # not closed
        self.voting.start_date = timezone.now() - datetime.timedelta(days=1)
        self.voting.save()
        self.voting.end_date = timezone.now() + datetime.timedelta(days=1)
        self.voting.save()
        response = self.client.post('/store/', data, format='json')
        self.assertEqual(response.status_code, 200)

        # closed
        self.voting.end_date = timezone.now() - datetime.timedelta(days=1)
        self.voting.save()
        response = self.client.post('/store/', data, format='json')
        self.assertEqual(response.status_code, 401)
        
        
        
class StoreTextCase(BaseTestCase):
  
    def setUp(self):
        super().setUp()
        self.question = Question(desc='qwerty', type='C')
        self.question_text = Question(desc='qwerty', type='T')
        self.question.save()
        self.question_text.save()
        self.voting = Voting(pk=5001,
                             name='voting example',
                             question=self.question,
                             start_date=timezone.now(),
        )
        self.voting_text = Voting(pk=5002,
                             name='voting example text',
                             question=self.question_text,
                             start_date=timezone.now(),)
        self.voting.save()
        self.voting_text.save()


    def tearDown(self):
        self.question = None
        self.question_text = None
        self.voting = None
        self.voting_text = None
        super().tearDown()


    def get_or_create_user(self, pk):
        user, _ = User.objects.get_or_create(pk=pk)
        user.username = 'user{}'.format(pk)
        user.set_password('qwerty')
        user.save()
        return user

    def test_store_vote_text(self):
        CTE_A = 96
        CTE_B = 184

        user = self.get_or_create_user(1)
        census = Census(voting_id=self.voting_text.id, voter_id=1)
        census.save()
        data = {
            "voting": self.voting_text.id,
            "voter": 1,
            "vote": { "a": CTE_A, "b": CTE_B },
            'voting_type': 'comment'
        }
        self.login(user=user.username)
        response = self.client.post('/store/', data, format='json')
        self.assertEqual(response.status_code, 200)

        self.assertEqual(Vote.objects.count(), 1)
        self.assertEqual(Vote.objects.first().voting_id, self.voting_text.id)
        self.assertEqual(Vote.objects.first().voter_id, 1)
        self.assertEqual(Vote.objects.first().a, CTE_A)
        self.assertEqual(Vote.objects.first().b, CTE_B)
          
class StoreYesNoCase(BaseTestCase):
          
    def setUp(self):
        super().setUp()
        self.question = Question(desc='qwerty', type="C")
        self.question_yesno = Question(desc='qwerty', type='Y')
        self.question.save()
        self.question_yesno.save()
        self.voting = Voting(pk=5001,
                             name='voting example',
                             question=self.question,
                             start_date=timezone.now(),
        )
        self.voting_yesno = Voting(pk=5002,
                             name='voting example yesno',
                             question=self.question_yesno,
                             start_date=timezone.now(),)
        self.voting.save()
        self.voting_yesno.save()

    def tearDown(self):
        self.question = None
        self.question_yesno = None
        self.voting = None
        self.voting_yesno = None
        super().tearDown()

    def get_or_create_user(self, pk):
        user, _ = User.objects.get_or_create(pk=pk)
        user.username = 'user{}'.format(pk)
        user.set_password('qwerty')
        user.save()
        return user
          
    def test_store_vote_yesno(self):
        CTE_A = 96
        CTE_B = 184

        user = self.get_or_create_user(1)
        census = Census(voting_id=self.voting_yesno.id, voter_id=1)
        census.save()
        data = {
            "voting": self.voting_yesno.id,
            "voter": 1,
            "vote": { "a": CTE_A, "b": CTE_B },
            'voting_type': 'yesno'
        }
        self.login(user=user.username)
        response = self.client.post('/store/', data, format='json')
        self.assertEqual(response.status_code, 200)

        self.assertEqual(Vote.objects.count(), 1)
        self.assertEqual(Vote.objects.first().voting_id, self.voting_yesno.id)
        self.assertEqual(Vote.objects.first().voter_id, 1)
        self.assertEqual(Vote.objects.first().a, CTE_A)
        self.assertEqual(Vote.objects.first().b, CTE_B)


class StorePreferenceCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.question = Question(desc='qwerty', type="C")
        self.question_preference = Question(desc='qwerty', type='R')
        self.question.save()
        self.question_preference.save()
        self.voting = Voting(pk=5001,
                             name='voting example',
                             question=self.question,
                             start_date=timezone.now(),
        )
        self.voting_preference = Voting(pk=5002,
                             name='voting example text',
                             question=self.question_preference,
                             start_date=timezone.now(),)
        self.voting.save()
        self.voting_preference.save()

    def tearDown(self):
        self.question = None
        self.question_preference = None
        self.voting = None
        self.voting_preference = None
        super().tearDown()

    def get_or_create_user(self, pk):
        user, _ = User.objects.get_or_create(pk=pk)
        user.username = 'user{}'.format(pk)
        user.set_password('qwerty')
        user.save()
        return user


    def test_store_vote_preference(self):
        CTE_A = 96
        CTE_B = 184
        
        user = self.get_or_create_user(1)
        census = Census(voting_id=self.voting_preference.id, voter_id=1)
        census.save()
        data = {
            "voting": self.voting_preference.id,
            "voter": 1,
            "vote": { "a": CTE_A, "b": CTE_B },
            'voting_type': 'preference'
        }
        self.login(user=user.username)
        response = self.client.post('/store/', data, format='json')
        self.assertEqual(response.status_code, 200)

        self.assertEqual(Vote.objects.count(), 1)
        self.assertEqual(Vote.objects.first().voting_id, self.voting_preference.id)
        self.assertEqual(Vote.objects.first().voter_id, 1)
        self.assertEqual(Vote.objects.first().a, CTE_A)
        self.assertEqual(Vote.objects.first().b, CTE_B)

    def test_voting_invalid_type(self):
        user = self.get_or_create_user(2)
        census = Census(voting_id=self.voting_preference.id, voter_id=2)
        census.save()
        data = {
            "voting": self.voting_preference.id,
            "voter": 1,
            "vote": { "a": 1, "b": 1 },
            'voting_type': 'invalid'
        }
        self.login(user=user.username)
        response = self.client.post('/store/', data, format='json')
        self.assertEqual(response.status_code, 400)