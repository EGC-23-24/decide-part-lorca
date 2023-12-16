import random
import itertools
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import TestCase
from nose.tools import nottest

from selenium import webdriver
from selenium.webdriver.common.by import By

from base import mods
from base.tests import BaseTestCase
from census.models import Census
from mixnet.mixcrypt import ElGamal
from mixnet.mixcrypt import MixCrypt
from mixnet.models import Auth
from voting.models import Voting, Question, QuestionOption, QuestionOptionRanked, QuestionOptionYesNo


class VotingTestCase(BaseTestCase):

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def encrypt_msg(self, msg, v, bits=settings.KEYBITS):
        pk = v.pub_key
        p, g, y = (pk.p, pk.g, pk.y)
        k = MixCrypt(bits=bits)
        k.k = ElGamal.construct((p, g, y))
        return k.encrypt(msg)

    def store_yesno_votes(self, v):
        voters = list(Census.objects.filter(voting_id=v.id))
        voter = voters.pop()

        clear = {}
        for opt in v.question.options.all():
            clear[opt.number] = 0
            for i in range(random.randint(0, 5)):
                a, b = self.encrypt_msg(opt.number, v)
                data = {
                    'voting': v.id,
                    'voter': voter.voter_id,
                    'voting_type': 'classic',
                    'vote': {'a': a, 'b': b},
                }
                clear[opt.number] += 1
                user = self.get_or_create_user(voter.voter_id)
                self.login(user=user.username)
                voter = voters.pop()
                mods.post('store', json=data)
        return clear

    def create_classic_voting(self):
        q = Question(desc='test question', type='C')
        q.save()
        for i in range(5):
            opt = QuestionOption(question=q, option='option {}'.format(i+1))
            opt.save()
        v = Voting(name='test voting', question=q)
        v.save()

        a, _ = Auth.objects.get_or_create(url=settings.BASEURL,
                                          defaults={'me': True, 'name': 'test auth'})
        a.save()
        v.auths.add(a)

        return v

    def create_ranked_voting(self):
        q = Question(desc='ranked test question', type='R')
        q.save()
        for i in range(5):
            opt = QuestionOptionRanked(
                question=q, option='option {}'.format(i+1))
            opt.save()
        v = Voting(name='test ranked voting', question=q)
        v.save()

        a, _ = Auth.objects.get_or_create(url=settings.BASEURL, defaults={
                                          'me': True, 'name': 'test auth'})
        a.save()
        v.auths.add(a)

        return v

    def create_yesno_voting(self):
        q = Question(desc='Yes/No test question', type='Y')
        q.save()
        for i in range(5):
            opt = QuestionOptionYesNo(
                question=q, option='option {}'.format(i+1))
            opt.save()
        v = Voting(name='test Yes/No voting', question=q)
        v.save()

        a, _ = Auth.objects.get_or_create(url=settings.BASEURL, defaults={
                                          'me': True, 'name': 'test auth'})
        a.save()
        v.auths.add(a)

        return v

    def create_multiple_choice_voting(self):
        q = Question(desc='test multiple choice question', type='M')
        q.save()
        for i in range(5):
            opt = QuestionOption(question=q, option='option {}'.format(i+1))
            opt.save()
        v = Voting(name='test voting', question=q)
        v.save()

        a, _ = Auth.objects.get_or_create(url=settings.BASEURL,
                                          defaults={'me': True, 'name': 'test auth'})
        a.save()
        v.auths.add(a)

        return v

    def create_comment_voting(self):
        q = Question(desc='Text test question', type='T')
        q.save()
        v = Voting(name='test text voting', question=q)
        v.save()

        a, _ = Auth.objects.get_or_create(url=settings.BASEURL, defaults={
                                          'me': True, 'name': 'test auth'})
        a.save()
        v.auths.add(a)

        return v

    def create_voters(self, v):
        for i in range(100):
            u, _ = User.objects.get_or_create(username='testvoter{}'.format(i))
            u.is_active = True
            u.save()
            c = Census(voter_id=u.id, voting_id=v.id)
            c.save()

    def get_or_create_user(self, pk):
        user, _ = User.objects.get_or_create(pk=pk)
        user.username = 'user{}'.format(pk)
        user.set_password('qwerty')
        user.save()
        return user

    def store_classic_votes(self, v):
        voters = list(Census.objects.filter(voting_id=v.id))
        voter = voters.pop()

        clear = {}
        for opt in v.question.options.all():
            clear[opt.number] = 0
            for i in range(random.randint(0, 5)):
                a, b = self.encrypt_msg(opt.number, v)
                data = {
                    'voting': v.id,
                    'voter': voter.voter_id,
                    'voting_type': 'classic',
                    'vote': {'a': a, 'b': b},
                    'voting_type': 'classic',
                }
                clear[opt.number] += 1
                user = self.get_or_create_user(voter.voter_id)
                self.login(user=user.username)
                voter = voters.pop()
                mods.post('store', json=data)
        return clear

    @nottest
    def test_complete_voting(self):
        v = self.create_classic_voting()
        self.create_voters(v)

        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()

        clear = self.store_classic_votes(v)

        self.login()  # set token
        v.tally_votes(self.token)

        tally = v.tally
        tally.sort()
        tally = {k: len(list(x)) for k, x in itertools.groupby(tally)}

        for q in v.question.options.all():
            self.assertEqual(tally.get(q.number, 0), clear.get(q.number, 0))

        for q in v.postproc:
            self.assertEqual(tally.get(q["number"], 0), q["votes"])

    def test_complete_ranked_voting(self):
        v = self.create_ranked_voting()
        self.create_voters(v)

        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()
        # clear = self.store_votes(v)

        self.login()
        # v.tally_votes(self.token)

        # tally = v.tally
        # tally.sort()
        # tally = {k: len(list(x)) for k, x in itertools.groupby(tally)}

        # for q in v.question.options.all():
        #     self.assertEqual(tally.get(q.number, 0), clear.get(q.number, 0))

        # for q in v.postproc:
        #     self.assertEqual(tally.get(q["number"], 0), q["votes"])

    def store_multiple_choice_votes(self, v):
        voters = list(Census.objects.filter(voting_id=v.id))
        voter = voters.pop()
        options = v.question.options.all()

        clear = {}

        for opt in v.question.options.all():
            clear[opt.number] = 0

        for i in range(random.randint(0, 5)):
            votes = []
            for j in range(random.randint(0, len(options))):
                a, b = self.encrypt_msg(options[j].number, v)
                choice = {'a': a, 'b': b}
                votes.append(choice)
                clear[options[j].number] += 1

            data = {
                'voting': v.id,
                'voter': voter.voter_id,
                'votes': votes,
                'voting_type': 'choices'
            }
            user = self.get_or_create_user(voter.voter_id)
            self.login(user=user.username)
            voter = voters.pop()
            mods.post('store', json=data)
        return clear

    def test_complete_multiple_choice_voting(self):
        v = self.create_multiple_choice_voting()
        self.create_voters(v)

        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()

        clear = self.store_multiple_choice_votes(v)

        self.login()  # set token
        v.tally_votes(self.token)

        tally = v.tally
        tally.sort()
        tally = {k: len(list(x)) for k, x in itertools.groupby(tally)}

        for q in v.question.options.all():
            self.assertEqual(tally.get(q.number, 0), clear.get(q.number, 0))

        for q in v.postproc:
            self.assertEqual(tally.get(q["number"], 0), q["votes"])

    def test_complete_comment_voting(self):
        v = self.create_comment_voting()
        self.create_voters(v)

        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()

        clear = self.store_classic_votes(v)

        self.login()

    def test_create_voting_from_api(self):
        data = {'name': 'Example'}
        response = self.client.post('/voting/', data, format='json')
        self.assertEqual(response.status_code, 401)

        # login with user no admin
        self.login(user='noadmin')
        response = mods.post('voting', params=data, response=True)
        self.assertEqual(response.status_code, 403)

        # login with user admin
        self.login()
        response = mods.post('voting', params=data, response=True)
        self.assertEqual(response.status_code, 400)

        data = {
            'name': 'Example',
            'desc': 'Description example',
            'question': 'I want a ',
            'question_opt': ['cat', 'dog', 'horse']
        }

        response = self.client.post('/voting/', data, format='json')
        self.assertEqual(response.status_code, 201)

    def test_complete_yesno_voting(self):
        v = self.create_yesno_voting()
        self.create_voters(v)

        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()

        clear = self.store_yesno_votes(v)

        self.login()
        v.tally_votes(self.token)

        tally = v.tally
        tally.sort()
        tally = {k: len(list(x)) for k, x in itertools.groupby(tally)}

        for q in v.question.options.all():
            self.assertEqual(tally.get(q.number, 0), clear.get(q.number, 0))

        for q in v.postproc:
            self.assertEqual(tally.get(q["number"], 0), q["votes"])

    def test_create_voting_from_api_ranked(self):
        data = {'name': 'Voting ranked'}
        response = self.client.post('/voting/', data, format='json')
        self.assertEqual(response.status_code, 401)

        # login with user no admin
        self.login(user='noadmin')
        response = mods.post('voting', params=data, response=True)
        self.assertEqual(response.status_code, 403)

        # login with user admin
        self.login()
        response = mods.post('voting', params=data, response=True)
        self.assertEqual(response.status_code, 400)

        data = {
            'name': 'Voting ranked',
            'desc': 'Description example',
            'question': {
                'desc': 'Choose your prefered option',
                'type': 'R'
            },
            'question_opt': ['cat', 'dog', 'horse']
        }
        response = self.client.post('/voting/', data, format='json')
        self.assertEqual(response.status_code, 201)

    def test_create_multiple_choice_voting_from_api(self):
        data = {'name': 'Example'}
        response = self.client.post('/voting/', data, format='json')
        self.assertEqual(response.status_code, 401)

        # login with user no admin
        self.login(user='noadmin')
        response = mods.post('voting', params=data, response=True)
        self.assertEqual(response.status_code, 403)

        # login with user admin
        self.login()
        response = mods.post('voting', params=data, response=True)
        self.assertEqual(response.status_code, 400)

        data = {
            'name': 'Example',
            'desc': 'Description example',
            'question': {
                'desc': 'I want a ',
                'type': 'M'
            },
            'question_opt': ['cat', 'dog', 'horse']
        }

        response = self.client.post('/voting/', data, format='json')
        self.assertEqual(response.status_code, 201)

    def test_create_voting_from_api_comment(self):
        data = {'name': 'Voting text'}
        response = self.client.post('/voting/', data, format='json')
        self.assertEqual(response.status_code, 401)

        # login with user no admin
        self.login(user='noadmin')
        response = mods.post('voting', params=data, response=True)
        self.assertEqual(response.status_code, 403)

        # login with user admin
        self.login()
        response = mods.post('voting', params=data, response=True)
        self.assertEqual(response.status_code, 400)

        data = {
            'name': 'Voting text',
            'desc': 'Description example',
            'question': {
                'desc': 'What do you enjoy doing in your free time?',
                'type': 'T'
            },
            'question_opt': []

        }

        response = self.client.post('/voting/', data, format='json')
        self.assertEqual(response.status_code, 201)

    def test_update_voting(self):
        voting = self.create_classic_voting()

        data = {'action': 'start'}
        # response = self.client.post('/voting/{}/'.format(voting.pk), data, format='json')
        # self.assertEqual(response.status_code, 401)

        # login with user no admin
        self.login(user='noadmin')
        response = self.client.put(
            '/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 403)

        # login with user admin
        self.login()
        data = {'action': 'bad'}
        response = self.client.put(
            '/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)

        # STATUS VOTING: not started
        for action in ['stop', 'tally']:
            data = {'action': action}
            response = self.client.put(
                '/voting/{}/'.format(voting.pk), data, format='json')
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json(), 'Voting is not started')

        data = {'action': 'start'}
        response = self.client.put(
            '/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Voting started')

        # STATUS VOTING: started
        data = {'action': 'start'}
        response = self.client.put(
            '/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 'Voting already started')

        data = {'action': 'tally'}
        response = self.client.put(
            '/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 'Voting is not stopped')

        data = {'action': 'stop'}
        response = self.client.put(
            '/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Voting stopped')

        # STATUS VOTING: stopped
        data = {'action': 'start'}
        response = self.client.put(
            '/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 'Voting already started')

        data = {'action': 'stop'}
        response = self.client.put(
            '/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 'Voting already stopped')

        data = {'action': 'tally'}
        response = self.client.put(
            '/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Voting tallied')

        # STATUS VOTING: tallied
        data = {'action': 'start'}
        response = self.client.put(
            '/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 'Voting already started')

        data = {'action': 'stop'}
        response = self.client.put(
            '/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 'Voting already stopped')

        data = {'action': 'tally'}
        response = self.client.put(
            '/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 'Voting already tallied')


class QuestionTestCases(BaseTestCase):

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def createClassicQuestionSuccess(self):
        self.cleaner.get(self.live_server_url+"/admin/login/?next=/admin/")
        self.cleaner.set_window_size(1280, 720)

    def test_question_to_string(self):
        q = Question(desc='test question', type='C')
        self.assertEqual(str(q), 'test question')

    def test_question_option_to_string(self):
        q = Question(desc='test question', type='C')
        opt = QuestionOption(number=1, option='test option', question=q)
        self.assertEqual(str(opt), 'test option (1)')

    def test_question_option_ranked_to_string(self):
        q = Question(desc='test question', type='R')
        opt = QuestionOptionRanked(number=1, option='test option', question=q)
        self.assertEqual(str(opt), 'test option (1)')

    def test_question_option_ranked_error_str(self):
        q = Question(desc='test question', type='C')
        opt = QuestionOptionRanked(number=1, option='test option', question=q)
        self.assertEqual(str(opt),
                         'You cannot create a ranked option for a non-ranked question')

    def test_question_option_error_str(self):
        q = Question(desc='test question', type='R')
        opt = QuestionOption(number=1, option='test option', question=q)
        self.assertEqual(str(opt),
                         'You cannot create an option for a non-Classic or multiple choice question')

    def test_question_option_yesno_to_string(self):
        q = Question(desc='test question', type='Y')
        opt = QuestionOptionYesNo(number=1, option='test option', question=q)
        self.assertEqual(str(opt), 'test question - test option (1) ')

    def test_question_option_yesno_error_str(self):
        q = Question(desc='test question', type='C')
        opt = QuestionOptionYesNo(number=1, option='test option', question=q)
        self.assertEqual(str(opt),
                         'You cannot create a Yes/No option for a non-Yes/No question')

    def test_yes_no_question_option_error_str(self):
        q = Question(desc='test question', type='Y')
        opt = QuestionOption(number=1, option='test option', question=q)
        self.assertEqual(str(opt),
                         'You cannot create an option for a non-Classic or multiple choice question')

    def test_question(self):
        q1 = Question(desc='test question', type='C')
        q1.save()

        q2 = Question(desc='test question', type='Y')
        q2.save()

        q3 = Question(desc='test question', type='T')
        q3.save()

        q4 = Question(desc='test question', type='R')
        q4.save()

        self.assertEqual(q1.type, 'C')
        self.assertEqual(q2.type, 'Y')
        self.assertEqual(q3.type, 'T')
        self.assertEqual(q4.type, 'R')

        self.assertEqual(q1.desc, 'test question')
        self.assertEqual(q2.desc, 'test question')
        self.assertEqual(q3.desc, 'test question')
        self.assertEqual(q4.desc, 'test question')

    def test_question_option(self):
        Question(desc='test question', type='C').save()
        q = Question.objects.get(desc='test question')
        QuestionOption(number=1, option='test option', question=q).save()
        opt = QuestionOption.objects.get(option='test option')

        self.assertEqual(opt.number, 1)
        self.assertEqual(opt.option, 'test option')
        self.assertEqual(opt.question, q)

    def test_question_option_error(self):
        Question(desc='test question', type='R').save()
        q = Question.objects.get(desc='test question')
        QuestionOption(number=1, option='test option', question=q).save()
        self.assertRaises(QuestionOption.DoesNotExist)

    def test_question_option_ranked(self):
        Question(desc='test question', type='R').save()
        q = Question.objects.get(desc='test question')
        QuestionOptionRanked(number=1, option='test option', question=q).save()
        opt = QuestionOptionRanked.objects.get(option='test option')

        self.assertEqual(opt.number, 1)
        self.assertEqual(opt.option, 'test option')
        self.assertEqual(opt.question, q)

    def test_question_option_ranked_error(self):
        Question(desc='test question', type='C').save()
        q = Question.objects.get(desc='test question')
        QuestionOptionRanked(number=1, option='test option', question=q).save()
        self.assertRaises(QuestionOptionRanked.DoesNotExist)

    def test_question_option_yesno(self):
        Question(desc='test question', type='Y').save()
        q = Question.objects.get(desc='test question')
        QuestionOptionYesNo(number=1, option='test option', question=q).save()
        opt = QuestionOptionYesNo.objects.get(option='test option')

        self.assertEqual(opt.number, 1)
        self.assertEqual(opt.option, 'test option')
        self.assertEqual(opt.question, q)

    def test_question_option_error(self):
        Question(desc='test question', type='Y').save()
        q = Question.objects.get(desc='test question')
        QuestionOption(number=1, option='test option', question=q).save()
        self.assertRaises(QuestionOption.DoesNotExist)

    def test_question_option_yesno_error(self):
        Question(desc='test question', type='C').save()
        q = Question.objects.get(desc='test question')
        QuestionOptionYesNo(number=1, option='test option', question=q).save()
        self.assertRaises(QuestionOptionYesNo.DoesNotExist)

    def test_question_option_comment_error_str(self):
        q = Question(desc='test question', type='T')
        opt = QuestionOption(number=1, option='test option', question=q)
        self.assertEqual(str(opt),
                         'You cannot create an option for a non-Classic or multiple choice question')

@nottest
class PostProcTest(TestCase):
    def setUp(self):
        super().setUp()
    def tearDown(self):
        super().tearDown()

    def test_do_comment_postproc(self):
        q1 = Question(desc='test question 1', type='T')
        q1.save()

        v = Voting(name='test voting', question=q1)
        v.save()
    
        a, _ = Auth.objects.get_or_create(url=settings.BASEURL,
                                          defaults={'me': True, 'name': 'test auth'})
        a.save()
        v.auths.add(a)

        tally = {'msgs': ['text1', 'text2']}
        
        v.tally = tally
        v.save()

        v.do_postproc()

        self.assertEqual(v.postproc[0]['postproc'], 'text1')
        self.assertEqual(v.postproc[1]['postproc'], 'text2')

    def test_do_comment_postproc_no_votes(self):
        q1 = Question(desc='test question 1', type='T')
        q1.save()

        v = Voting(name='test voting', question=q1)
        v.save()
    
        a, _ = Auth.objects.get_or_create(url=settings.BASEURL,
                                          defaults={'me': True, 'name': 'test auth'})
        a.save()
        v.auths.add(a)

        tally = []

        v.tally = tally
        v.save()

        with self.assertRaises(AttributeError):
            v.do_postproc()

    def test_do_ranked_postproc(self):
        q = Question(desc='test question', type='R')
        q.save()
        op1 = QuestionOptionRanked(question=q, option='Test 1', number=1)
        op2 = QuestionOptionRanked(question=q, option='Test 2', number=2)
        op1.save()
        op2.save()
        v = Voting(name='test voting', question=q)
        v.save()
        a, _ = Auth.objects.get_or_create(url=settings.BASEURL,
                                          defaults={'me': True, 'name': 'test auth'})
        a.save()
        v.auths.add(a)

        tally = {
            'msgs': ['1-2', '2-1']
        }
        v.tally = tally
        v.save()

        v.do_postproc()

        self.assertEqual(v.postproc[0]['votes'], 2)
        self.assertEqual(v.postproc[1]['votes'], 2)
        self.assertEqual(v.postproc[0]['postproc'], 3)
        self.assertEqual(v.postproc[1]['postproc'], 3)

    def test_do_ranked_postproc_invalid_vote(self):
        q = Question(desc='test question', type='R')
        q.save()
        op1 = QuestionOptionRanked(question=q, option='Test 1', number=1)
        op2 = QuestionOptionRanked(question=q, option='Test 2', number=2)
        op1.save()
        op2.save()
        v = Voting(name='test voting', question=q)
        v.save()
        a, _ = Auth.objects.get_or_create(url=settings.BASEURL,
                                          defaults={'me': True, 'name': 'test auth'})
        a.save()
        v.auths.add(a)

        tally = {
            'msgs': ['1-2', '2-x']
        }
        v.tally = tally
        v.save()

        with self.assertRaises(ValueError):
            v.do_postproc()
