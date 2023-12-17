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
    """
    Test case for storing votes with choices.

    This class tests the functionality of storing votes for different types of voting,
    including classic, choices, text, yes/no, and preference types.

    Attributes:
        question (Question): A Question object for classic type voting.
        question_choices (Question): A Question object for multiple choices type voting.
        voting (Voting): A Voting object for classic type voting.
        voting_choices (Voting): A Voting object for multiple choices type voting.
    """

    def setUp(self):
        """
        Set up necessary objects for testing.

        Creates Question and Voting objects for both classic and multiple choices type voting.
        """
        
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
        """
        Clean up after tests.

        Clears the created objects to ensure isolation of tests.
        """
        
        self.question = None
        self.question_choices = None
        self.voting = None
        self.voting_choices = None

        super().tearDown()

    def gen_voting(self, pk):
        """
        Generate a voting object for testing.

        Args:
            pk (int): Primary key for the voting object.

        Creates a Voting object with specified primary key and saves it to the database.
        """
        
        voting = Voting(pk=pk, name='v1', desc="v1 desc", question=self.question, start_date=timezone.now(),
                        end_date=timezone.now() + datetime.timedelta(days=1))
        voting.save()

    def get_or_create_user(self, pk):
        """
        Get an existing user or create a new one for testing.

        Args:
            pk (int): Primary key of the user.

        Returns:
            User: The fetched or created User object.
        """
        
        user, _ = User.objects.get_or_create(pk=pk)
        user.username = 'user{}'.format(pk)
        user.set_password('qwerty')
        user.save()
        return user

    def gen_votes(self):
        """
        Generate random votes for testing.

        Returns:
            tuple: A tuple containing lists of generated voting IDs and user IDs.
        """
        
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
                "vote": {"a": a, "b": b},
                "voting_type": 'classic',
            }
            response = self.client.post('/store/', data, format='json')
            self.assertEqual(response.status_code, 200)

        self.logout()
        return votings, users

    def test_gen_vote_invalid(self):
        """
        Test case for generating an invalid vote.

        This method sends a POST request with invalid vote data and expects to receive a 401 Unauthorized status code.

        Attributes:
            data (dict): A dictionary containing the invalid vote data.
        """

        data = {
            "voting": 1,
            "voter": 1,
            "vote": {"a": 1, "b": 1},
            "voting_type": 'classic',
        }
        response = self.client.post('/store/', data, format='json')
        self.assertEqual(response.status_code, 401)

    def test_store_vote(self):
        """
        Test case for storing a valid vote.

        This method creates a voting instance and a user, then sends a POST request to store a vote and expects to receive a 200 OK status code. It also checks the count and content of the Vote objects in the database to ensure the vote is stored correctly.

        Attributes:
            VOTING_PK (int): Primary key for the voting instance.
            CTE_A (int): Test constant for 'a' field in vote.
            CTE_B (int): Test constant for 'b' field in vote.
            data (dict): A dictionary containing the vote data.
        """
        
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
            "vote": {"a": CTE_A, "b": CTE_B},
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
        """
        Test case for storing multiple choice votes.

        This method tests the storage of multiple choice votes by creating relevant data, sending a POST request, and verifying the response and database records.

        Attributes:
            CTE_A (int): Test constant for 'a' field in vote.
            CTE_B (int): Test constant for 'b' field in vote.
            data (dict): A dictionary containing multiple votes data.
        """
        
        CTE_A = 96
        CTE_B = 184
        user = self.get_or_create_user(1)
        census = Census(voting_id=self.voting_choices.id, voter_id=1)
        census.save()
        data = {
            "voting": self.voting_choices.id,
            "voter": 1,
            "votes": [{"a": CTE_A, "b": CTE_B}, {"a": CTE_A + 1, "b": CTE_B + 1}],
            'voting_type': 'choices'
        }
        self.login(user=user.username)
        response = self.client.post('/store/', data, format='json')
        self.assertEqual(response.status_code, 200)

        self.assertEqual(Vote.objects.count(), 2)
        self.assertEqual(Vote.objects.first().voting_id,
                         self.voting_choices.id)
        self.assertEqual(Vote.objects.first().voter_id, 1)
        self.assertEqual(Vote.objects.filter(a=CTE_A).values()[0]['a'], CTE_A)
        self.assertEqual(Vote.objects.filter(b=CTE_B).values()[0]['b'], CTE_B)
        self.assertEqual(Vote.objects.filter(
            a=CTE_A + 1).values()[0]['a'], CTE_A + 1)
        self.assertEqual(Vote.objects.filter(
            b=CTE_B + 1).values()[0]['b'], CTE_B + 1)

    def test_voting_invalid_type(self):
        """
        Test case for storing a vote with an invalid voting type.

        This method attempts to store a vote with an invalid voting type and expects to receive a 400 Bad Request status code.

        Attributes:
            data (dict): A dictionary containing the vote data with an invalid voting type.
        """
        
        user = self.get_or_create_user(2)
        census = Census(voting_id=self.voting_choices.id, voter_id=2)
        census.save()
        data = {
            "voting": self.voting_choices.id,
            "voter": 1,
            "vote": {"a": 1, "b": 1},
            'voting_type': 'invalid'
        }
        self.login(user=user.username)
        response = self.client.post('/store/', data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_store_vote_text(self):
        """
        Test case for storing a text vote.

        This method tests storing a text-based vote by creating relevant data, sending a POST request, and verifying the response and database records.

        Attributes:
            CTE_A (int): Test constant for 'a' field in vote.
            CTE_B (int): Test constant for 'b' field in vote.
            data (dict): A dictionary containing the text vote data.
        """
        
        CTE_A = 96
        CTE_B = 184
        user = self.get_or_create_user(1)
        census = Census(voting_id=self.voting_choices.id, voter_id=1)
        census.save()
        data = {
            "voting": self.voting_choices.id,
            "voter": 1,
            "vote": {"a": CTE_A, "b": CTE_B},
            'voting_type': 'comment'
        }
        self.login(user=user.username)
        response = self.client.post('/store/', data, format='json')
        self.assertEqual(response.status_code, 200)

        self.assertEqual(Vote.objects.count(), 1)
        self.assertEqual(Vote.objects.first().voting_id,
                         self.voting_choices.id)
        self.assertEqual(Vote.objects.first().voter_id, 1)
        self.assertEqual(Vote.objects.first().a, CTE_A)
        self.assertEqual(Vote.objects.first().b, CTE_B)

    def test_voting_invalid_type(self):
        """
        Test case for retrieving stored votes.

        This method generates votes and then tests retrieving them via GET requests, verifying the response status codes and content.
        """
        
        user = self.get_or_create_user(2)
        census = Census(voting_id=self.voting_choices.id, voter_id=2)
        census.save()
        data = {
            "voting": self.voting_choices.id,
            "voter": 1,
            "vote": {"a": 1, "b": 1},
            'voting_type': 'invalid'
        }

        self.login(user=user.username)
        response = self.client.post('/store/', data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_vote(self):
        """
        Test case for retrieving stored votes.

        This method generates votes and then tests retrieving them via GET requests, verifying the response status codes and content.
        """
        
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
        self.assertEqual(votes[0], VoteSerializer(
            Vote.objects.all().first()).data)

    def test_filter(self):
        """
        Test case for filtering votes.

        This method generates votes and then tests filtering them by voting_id and voter_id via GET requests, verifying the response status codes and content.
        """
        
        votings, voters = self.gen_votes()
        v = votings[0]

        response = self.client.get(
            '/store/?voting_id={}'.format(v), format='json')
        self.assertEqual(response.status_code, 401)

        self.login(user='noadmin')
        response = self.client.get(
            '/store/?voting_id={}'.format(v), format='json')
        self.assertEqual(response.status_code, 403)

        self.login()
        response = self.client.get(
            '/store/?voting_id={}'.format(v), format='json')
        self.assertEqual(response.status_code, 200)
        votes = response.json()

        self.assertEqual(len(votes), Vote.objects.filter(voting_id=v).count())

        v = voters[0]
        response = self.client.get(
            '/store/?voter_id={}'.format(v), format='json')
        self.assertEqual(response.status_code, 200)
        votes = response.json()

        self.assertEqual(len(votes), Vote.objects.filter(voter_id=v).count())

    def test_hasvote(self):
        """
        Test case for checking if a specific vote exists.

        This method tests the existence of a specific vote by voter_id and voting_id, verifying the response status codes and content.
        """
    
        votings, voters = self.gen_votes()
        vo = Vote.objects.first()
        v = vo.voting_id
        u = vo.voter_id

        response = self.client.get(
            '/store/?voting_id={}&voter_id={}'.format(v, u), format='json')
        self.assertEqual(response.status_code, 401)

        self.login(user='noadmin')
        response = self.client.get(
            '/store/?voting_id={}&voter_id={}'.format(v, u), format='json')
        self.assertEqual(response.status_code, 403)

        self.login()
        response = self.client.get(
            '/store/?voting_id={}&voter_id={}'.format(v, u), format='json')
        self.assertEqual(response.status_code, 200)
        votes = response.json()

        self.assertEqual(len(votes), 1)
        self.assertEqual(votes[0]["voting_id"], v)
        self.assertEqual(votes[0]["voter_id"], u)

    def test_voting_status(self):
        """
        Test case for verifying voting status during vote storage.

        This method checks the response status code when attempting to store a vote based on the voting's opening and closing status.

        Attributes:
            data (dict): A dictionary containing the vote data.
        """
    
        data = {
            "voting": 5001,
            "voter": 1,
            "vote": {"a": 30, "b": 55},
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
    """
    Test case for storing text-type votes.

    Attributes:
        question (Question): A classic question instance for the test.
        question_text (Question): A text-type question instance for the test.
        voting (Voting): A voting instance associated with the classic question.
        voting_text (Voting): A voting instance associated with the text-type question.
    """

    def setUp(self):
        """
        Set up method to initialize test data before each test is run.
        """
        
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
        """
        Tear down method to clean up after each test is run.
        """
        
        self.question = None
        self.question_text = None
        self.voting = None
        self.voting_text = None
        super().tearDown()

    def get_or_create_user(self, pk):
        """
        Retrieves or creates a user for the given primary key.

        Args:
            pk (int): The primary key of the user.

        Returns:
            User: The retrieved or created user.
        """
        
        user, _ = User.objects.get_or_create(pk=pk)
        user.username = 'user{}'.format(pk)
        user.set_password('qwerty')
        user.save()
        return user

    def test_store_vote_text(self):
        """
        Tests the storage of a text-type vote.
        """
        
        CTE_A = 96
        CTE_B = 184

        user = self.get_or_create_user(1)
        census = Census(voting_id=self.voting_text.id, voter_id=1)
        census.save()
        data = {
            "voting": self.voting_text.id,
            "voter": 1,
            "vote": {"a": CTE_A, "b": CTE_B},
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
    """
    Test case for storing yes/no-type votes.

    Attributes:
        question (Question): A classic question instance for the test.
        question_yesno (Question): A yes/no-type question instance for the test.
        voting (Voting): A voting instance associated with the classic question.
        voting_yesno (Voting): A voting instance associated with the yes/no-type question.
    """

    def setUp(self):
        """
        Set up method to initialize test data before each test is run.
        """
        
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
        """
        Tear down method to clean up after each test is run.
        """
        
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
        """
        Tests the storage of a yes/no-type vote.
        """
        
        CTE_A = 96
        CTE_B = 184

        user = self.get_or_create_user(1)
        census = Census(voting_id=self.voting_yesno.id, voter_id=1)
        census.save()
        data = {
            "voting": self.voting_yesno.id,
            "voter": 1,
            "vote": {"a": CTE_A, "b": CTE_B},
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
    """
    Test case for storing preference-type votes.

    Attributes:
        question (Question): A classic question instance for the test.
        question_preference (Question): A preference-type question instance for the test.
        voting (Voting): A voting instance associated with the classic question.
        voting_preference (Voting): A voting instance associated with the preference-type question.
    """
    
    def setUp(self):
        """
        Set up method to initialize test data before each test is run.
        """
        
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
        """
        Tear down method to clean up after each test is run.
        """
        
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
        """
        Tests the storage of a preference-type vote.
        """
        
        CTE_A = 96
        CTE_B = 184

        user = self.get_or_create_user(1)
        census = Census(voting_id=self.voting_preference.id, voter_id=1)
        census.save()
        data = {
            "voting": self.voting_preference.id,
            "voter": 1,
            "vote": {"a": CTE_A, "b": CTE_B},
            'voting_type': 'preference'
        }
        self.login(user=user.username)
        response = self.client.post('/store/', data, format='json')
        self.assertEqual(response.status_code, 200)

        self.assertEqual(Vote.objects.count(), 1)
        self.assertEqual(Vote.objects.first().voting_id,
                         self.voting_preference.id)
        self.assertEqual(Vote.objects.first().voter_id, 1)
        self.assertEqual(Vote.objects.first().a, CTE_A)
        self.assertEqual(Vote.objects.first().b, CTE_B)

    def test_voting_invalid_type(self):
        """
        Tests the behavior when attempting to store a vote with an invalid voting type.
        """
        
        user = self.get_or_create_user(2)
        census = Census(voting_id=self.voting_preference.id, voter_id=2)
        census.save()
        data = {
            "voting": self.voting_preference.id,
            "voter": 1,
            "vote": {"a": 1, "b": 1},
            'voting_type': 'invalid'
        }
        self.login(user=user.username)
        response = self.client.post('/store/', data, format='json')
        self.assertEqual(response.status_code, 400)
