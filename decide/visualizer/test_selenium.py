from base.tests import BaseTestCase
from census.models import Census
from voting.models import QuestionOptionYesNo, Voting, Question, QuestionOption
from django.utils import timezone
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from mixnet.models import Auth
from selenium import webdriver
from selenium.webdriver.common.by import By
from django.conf import settings
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from base import mods
from django.contrib.auth.models import User

class VisualizerTestCase(StaticLiveServerTestCase):
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
    
    def create_yesno_voting_started(self):
        q = Question(desc='Yes/No test question', type='Y')
        q.save()
        for i in range(5):
            opt = QuestionOptionYesNo(question=q, option='option {}'.format(i+1))
            opt.save()
        v = Voting(name='test Yes/No voting', question=q)
        v.save()

        a, _ = Auth.objects.get_or_create(url=settings.BASEURL,defaults={'me': True, 'name': 'test auth'})
        a.save()
        v.auths.add(a)
        v.start_date = timezone.now()
        return v

    def create_multiple_choice_voting_started(self):
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
        v.start_date = timezone.now()

        return v

    def create_comment_voting_started(self):
        q = Question(desc='Text test question', type='T')
        q.save()
        v = Voting(name='test text voting', question=q)
        v.save()

        a, _ = Auth.objects.get_or_create(url=settings.BASEURL,defaults={'me': True, 'name': 'test auth'})
        a.save()
        v.auths.add(a)
        v.start_date = timezone.now()

        return v
    
    def setUp(self):
        self.base = BaseTestCase()
        self.base.setUp()

        options = webdriver.ChromeOptions()
        options.headless = True
        self.driver = webdriver.Chrome(options=options)
            
    def tearDown(self):           
        super().tearDown()
        
        self.driver.quit()
        self.base.tearDown()
            
    def test_visualizer_not_started(self):        
        voting = self.create_classic_voting()
        voting.save()

        self.driver.get(f'{self.live_server_url}/visualizer/{voting.pk}/')
        voting_state= self.driver.find_element(By.TAG_NAME,"h2").text
        
        self.assertEqual(voting_state, "Voting not started")
    
    def test_visualizer_started_no_census(self):        
        question = Question(desc='test question', type='C')
        question.save()
        voting = Voting(name='test voting', start_date=timezone.now(), question_id=question.id)
        voting.save()

        self.driver.get(f'{self.live_server_url}/visualizer/{voting.pk}/')
        self.assertEqual(self.driver.find_element(By.ID, "participation").text, "-")

    def test_visualizer_census_change(self):        
        question = Question(desc='test question', type='C')
        question.save()
        for i in range(5):
            opt = QuestionOption(question=question, option="option {}".format(i + 1))
            opt.save()
        voting = Voting(name="test voting",start_date=timezone.now(), question=question)
        voting.save()
        
        self.driver.get(f'{self.live_server_url}/visualizer/{voting.pk}/')
        census_before = self.driver.find_element(By.ID, "census").text

        user, created = User.objects.get_or_create(username='testvoter')
        user.is_active = True
        user.save()

        census1 = Census.objects.create(voting_id=voting.id, voter_id=user.id)

        user2, created2 = User.objects.get_or_create(username='testvoter2')
        user2.is_active = True
        user2.save()

        census2 = Census.objects.create(voting_id=voting.id, voter_id=user2.id)

        self.driver.get(f'{self.live_server_url}/visualizer/{voting.pk}/')
        census_after = self.driver.find_element(By.ID, "census").text

        self.assertNotEqual(census_before, census_after)

    def test_visualizer_started_classic_with_census(self):        
        question = Question(desc="test question", type="C")
        question.save()
        for i in range(5):
            opt = QuestionOption(question=question, option="option {}".format(i + 1))
            opt.save()
        voting = Voting(name="test voting",start_date=timezone.now(), question=question)
        voting.save()

        user, created = User.objects.get_or_create(username='testvoter')
        user.is_active = True
        user.save()

        census1 = Census.objects.create(voting_id=voting.id, voter_id=user.id)

        user2, created2 = User.objects.get_or_create(username='testvoter2')
        user2.is_active = True
        user2.save()

        census2 = Census.objects.create(voting_id=voting.id, voter_id=user2.id)

        self.driver.get(f'{self.live_server_url}/visualizer/{voting.pk}/')
        self.assertEqual(self.driver.find_element(By.ID, "participation").text, "0.0%")
        
        
    def test_visualizer_classic_finished(self):        
        question = Question(desc='test question', type='C')
        question.save()
        voting = Voting(name='test voting', start_date=timezone.now(), end_date=timezone.now() + timezone.timedelta(days=1), question_id=question.id)
        voting.save()

        self.driver.get(f'{self.live_server_url}/visualizer/{voting.pk}/')
        
        chart_select = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "chart-select"))
        )
        
        chart_select = Select(chart_select)

        default_option = chart_select.first_selected_option.text
        self.assertEqual(default_option, "Doughnut Chart (Score)")

        chart_options = [
            ("Polar Chart (Score)", "polar-chart-post"),
            ("Polar Chart (Votes)", "polar-chart-votes"),
            ("Radar Chart (Score)", "radar-chart-post"),
            ("Radar Chart (Votes)", "radar-chart-votes"),
            ("Bar Chart", "bar-chart"),
            ("Doughnut Chart (Votes)", "doughnut-chart-votes"),
        ]

        for option_text, chart_id in chart_options:
            chart_select.select_by_visible_text(option_text)
            
            selected_option = chart_select.first_selected_option.text
            self.assertEqual(selected_option, option_text)

            chart_element = self.driver.find_element(By.ID, chart_id)
            self.assertTrue(chart_element.is_displayed())

    def test_visualizer_started_yesno_with_census(self):        
        voting = self.create_yesno_voting_started()
        voting.save()

        user, created = User.objects.get_or_create(username='testvoter')
        user.is_active = True
        user.save()

        census1 = Census.objects.create(voting_id=voting.id, voter_id=user.id)

        user2, created2 = User.objects.get_or_create(username='testvoter2')
        user2.is_active = True
        user2.save()

        census2 = Census.objects.create(voting_id=voting.id, voter_id=user2.id)

        self.driver.get(f'{self.live_server_url}/visualizer/{voting.pk}/')
        self.assertEqual(self.driver.find_element(By.ID, "participation").text, "0.0%")

    def test_visualizer_yesno_finished(self):        
        voting = self.create_yesno_voting_started()
        voting.end_date = timezone.now() + timezone.timedelta(days=1)
        voting.save()

        self.driver.get(f'{self.live_server_url}/visualizer/{voting.pk}/')
        voting_state= self.driver.find_element(By.TAG_NAME,"h3").text
        self.assertEqual(voting_state, "Yes/No voting Results:")
        
        chart_select = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "chart-select"))
        )
        
        chart_select = Select(chart_select)

        default_option = chart_select.first_selected_option.text
        self.assertEqual(default_option, "Bar Chart")

        chart_option = ("Polar Chart (Score)", "polar-chart-post")

        chart_select.select_by_visible_text(chart_option[0])
        
        selected_option = chart_select.first_selected_option.text
        self.assertEqual(selected_option, chart_option[0])

        chart_element = self.driver.find_element(By.ID, chart_option[1])
        self.assertTrue(chart_element.is_displayed())
        
    def test_visualizer_started_comment_with_census(self):        
        voting = self.create_comment_voting_started()
        voting.save()

        user, created = User.objects.get_or_create(username='testvoter')
        user.is_active = True
        user.save()

        census1 = Census.objects.create(voting_id=voting.id, voter_id=user.id)

        user2, created2 = User.objects.get_or_create(username='testvoter2')
        user2.is_active = True
        user2.save()

        census2 = Census.objects.create(voting_id=voting.id, voter_id=user2.id)

        self.driver.get(f'{self.live_server_url}/visualizer/{voting.pk}/')
        self.assertEqual(self.driver.find_element(By.ID, "participation").text, "0.0%")
        
    def test_visualizer_comment_finished(self):        
        voting = self.create_comment_voting_started()
        voting.end_date = timezone.now() + timezone.timedelta(days=1)
        voting.save()

        self.driver.get(f'{self.live_server_url}/visualizer/{voting.pk}/')
        
        voting_state= self.driver.find_element(By.TAG_NAME,"h3").text
        self.assertEqual(voting_state, "Text Voting Results:")
        
        select_elements = self.driver.find_elements(By.TAG_NAME, "select")
        self.assertEqual(len(select_elements), 0)
        
    def test_visualizer_started_multiple_choice_with_census(self):        
        voting = self.create_multiple_choice_voting_started()
        voting.save()

        user, created = User.objects.get_or_create(username='testvoter')
        user.is_active = True
        user.save()

        census1 = Census.objects.create(voting_id=voting.id, voter_id=user.id)

        user2, created2 = User.objects.get_or_create(username='testvoter2')
        user2.is_active = True
        user2.save()

        census2 = Census.objects.create(voting_id=voting.id, voter_id=user2.id)

        self.driver.get(f'{self.live_server_url}/visualizer/{voting.pk}/')
        self.assertEqual(self.driver.find_element(By.ID, "participation").text, "0.0%")

    def test_visualizer_multiple_choice_finished(self):        
        voting = self.create_multiple_choice_voting_started()
        voting.end_date = timezone.now() + timezone.timedelta(days=1)
        voting.save()

        self.driver.get(f'{self.live_server_url}/visualizer/{voting.pk}/')
        
        chart_select = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "chart-select"))
        )
        
        chart_select = Select(chart_select)

        default_option = chart_select.first_selected_option.text
        self.assertEqual(default_option, "Doughnut Chart (Score)")

        chart_options = [
            ("Polar Chart (Score)", "polar-chart-post"),
            ("Polar Chart (Votes)", "polar-chart-votes"),
            ("Radar Chart (Score)", "radar-chart-post"),
            ("Radar Chart (Votes)", "radar-chart-votes"),
            ("Bar Chart", "bar-chart"),
            ("Doughnut Chart (Votes)", "doughnut-chart-votes"),
        ]

        for option_text, chart_id in chart_options:
            chart_select.select_by_visible_text(option_text)
            
            selected_option = chart_select.first_selected_option.text
            self.assertEqual(selected_option, option_text)

            chart_element = self.driver.find_element(By.ID, chart_id)
            self.assertTrue(chart_element.is_displayed())

