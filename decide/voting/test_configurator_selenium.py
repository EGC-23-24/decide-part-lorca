from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from base.tests import BaseTestCase

from selenium import webdriver
from selenium.webdriver.common.by import By
from django.utils import timezone

from django.contrib.auth.models import User
from rest_framework.test import APIClient
from base import mods
from nose.tools import nottest
from django.conf import settings
from base.tests import BaseTestCase
from census.models import Census
from mixnet.models import Auth
from voting.models import Voting, Question
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

@nottest
class ConfiguratorTests(StaticLiveServerTestCase):

    def setUp(self):
        # Load base test functionality for decide
        self.base = BaseTestCase()
        self.client = APIClient()
        self.token = None
        mods.mock_query(self.client)

        options = webdriver.ChromeOptions()
        options.headless = True
        self.driver = webdriver.Chrome(options=options)

        super().setUp()

    def tearDown(self):
        super().tearDown()
        self.driver.quit()

        self.base.tearDown()

    def create_yesno_voting(self):
        q = Question(desc='Yes/No test question', type='Y')
        q.save()
        v = Voting(name='test Yes/No voting', question=q)
        v.save()
        a, _ = Auth.objects.get_or_create(url=settings.BASEURL, defaults={
                                          'me': True, 'name': 'test auth'})
        a.save()
        v.auths.add(a)
        self.yesno_voting = v
        return v
    
    def create_users(self):
        user_admin = User(username='admin', is_staff=True, is_superuser=True)
        user_admin.set_password('qwerty')
        user_admin.save()
        user_noadmin = User(username='noadmin', is_staff=False)
        user_noadmin.set_password('qwerty')
        user_noadmin.save()
        return user_noadmin

    def add_user_to_census(self,pk):
        user = self.create_users()
        c = Census(voter_id=user.id, voting_id=self.yesno_voting.id)
        c.save()
        return c
    
    def test_access_to_voting_lists_view_as_admin(self):
        self.create_yesno_voting()
        self.add_user_to_census(1)
        self.driver.get(f'{self.live_server_url}/')
        signin_url = self.driver.find_element(By.ID, "login").get_dom_attribute('href')
        self.driver.get(f'{self.live_server_url}{signin_url}')
        username = WebDriverWait(self.driver, 10).until(
        EC.element_to_be_clickable((By.ID, "id_username"))
            )
        username.click()
        self.driver.find_element(By.ID, "id_username").send_keys("admin")
        self.driver.find_element(By.ID, "id_password1").click()
        self.driver.find_element(By.ID, "id_password1").send_keys("qwerty")
        self.driver.find_element(By.CLASS_NAME, "btn-primary").click()
        self.assertTrue(self.driver.current_url ==
                        f'{self.live_server_url}/')
        self.assertTrue(self.driver.find_element(By.ID, "listvoting").is_displayed())
        list_voting_url = self.driver.find_element(By.ID, "listvoting").get_dom_attribute('href')
        self.driver.get(f'{self.live_server_url}{list_voting_url}')
   
    def test_access_to_voting_lists_view_as_user(self):
        v = self.create_yesno_voting()
        self.add_user_to_census(1)
        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()
        self.driver.get(f'{self.live_server_url}/')
        signin_url = self.driver.find_element(By.ID, "login").get_dom_attribute('href')
        self.driver.get(f'{self.live_server_url}{signin_url}')
        username = WebDriverWait(self.driver, 10).until(
        EC.element_to_be_clickable((By.ID, "id_username"))
            )
        username.click()
        self.driver.find_element(By.ID, "id_username").send_keys("noadmin")
        self.driver.find_element(By.ID, "id_password1").click()
        self.driver.find_element(By.ID, "id_password1").send_keys("qwerty")
        self.driver.find_element(By.CLASS_NAME, "btn-primary").click()
        self.assertTrue(self.driver.current_url ==
                        f'{self.live_server_url}/')
        self.assertTrue(self.driver.find_element(By.ID, "listvoting").is_displayed())
        list_voting_url = self.driver.find_element(By.ID, "listvoting").get_dom_attribute('href')
        self.driver.get(f'{self.live_server_url}{list_voting_url}')
        self.assertTrue(self.driver.find_element(By.XPATH, "//a[contains(.,'Vote')]").is_displayed())
   
    def test_start_voting_from_votings_list(self):
        self.test_access_to_voting_lists_view_as_admin()
        self.driver.find_element(By.XPATH, "//button[contains(.,'Start')]").click()
        self.assertTrue(self.driver.find_element(By.XPATH, "//button[contains(.,'End')]").is_displayed())
    
    def test_stop_voting_from_votings_list(self):
        self.test_access_to_voting_lists_view_as_admin()
        self.driver.find_element(By.XPATH, "//button[contains(.,'Start')]").click()
        self.driver.find_element(By.XPATH, "//button[contains(.,'End')]").click()
        self.assertTrue(self.driver.find_element(By.XPATH, "//button[contains(.,'Tally')]").is_displayed())
    
    def test_update_voting_from_votings_list(self):
        self.test_access_to_voting_lists_view_as_admin()
        self.driver.find_element(By.XPATH, "//button[contains(.,'Update')]").click()
        self.driver.find_element(By.ID, "id_name").click()
        self.driver.find_element(By.ID, "id_name").send_keys("Yes/No voting UPDATED")
        self.driver.find_element(By.ID,"id_desc").click()
        self.driver.find_element(By.ID,"id_desc").send_keys("Description UPDATED")
        self.driver.find_element(By.ID, "id_question").click()
        self.driver.find_element(By.ID, "id_question").send_keys("Yes/No test question")
        self.driver.find_element(By.XPATH, "//button[contains(.,'Update')]").click()
        updated_element = self.driver.find_element(By.XPATH, "//h1[contains(.,'UPDATED')]").text
        self.assertTrue(updated_element.__contains__("Yes/No voting UPDATED"))

    def test_results_from_voting_list(self):
        self.test_access_to_voting_lists_view_as_admin()
        self.driver.find_element(By.XPATH, "//button[contains(.,'Start')]").click()
        self.driver.find_element(By.XPATH, "//button[contains(.,'End')]").click()
        self.assertTrue(self.driver.find_element(By.XPATH, "//a[contains(.,'Results')]").is_displayed())
        self.driver.find_element(By.XPATH, "//a[contains(.,'Results')]").click()
        self.assertTrue(self.driver.current_url.__contains__("/visualizer/"))
        self.assertTrue(self.driver.find_element(By.XPATH, "//h3[contains(.,'Yes/No voting Results:')]").is_displayed())