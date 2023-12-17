from django.conf import settings
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from nose.tools import nottest

from django.utils import timezone

from base.tests import BaseTestCase
import time
from census.models import Census
from voting.models import Question, Voting, Auth, QuestionOptionRanked, QuestionOption, QuestionOptionYesNo
from django.contrib.auth.models import User


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait

@nottest
class MultipleChoiceQuestionBoothTest(StaticLiveServerTestCase):
    """
    Selenium-based test case for the Multiple Choice Question booth in the voting app.

    This test case covers the behavior of the Multiple Choice Question booth, including
    the setup, user creation, and the interaction with the web interface.

    :ivar base: An instance of BaseTestCase for common test setup and teardown.
    :vartype base: BaseTestCase
    :ivar v: The Voting instance created for testing.
    :vartype v: Voting
    :ivar driver: The Selenium WebDriver instance for browser automation.
    :vartype driver: webdriver.Chrome
    """
    def create_voting(self):
        """
        Create a test voting with a multiple-choice question and options.

        :return: The created Voting instance.
        :rtype: Voting
        """
        q = Question(desc='test question')
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
    
    def get_or_create_user(self, pk):
        """
        Get or create a test user.

        :param pk: The primary key for the user.
        :type pk: int
        :return: The User instance.
        :rtype: User
        """
        user, _ = User.objects.get_or_create(pk=pk)
        user.username = 'user{}'.format(pk)
        user.set_password('qwerty')
        user.save()
        return user
      
    def setUp(self):
        """
        Set up the test environment before each test method is run.

        This method is called before each test method in the test case.

        :return: None
        """
        self.base = BaseTestCase()
        self.base.setUp()
        
        self.v = self.create_voting()
        self.v.question.type = 'M'
        self.v.question.save()

        #Añadimos al usuario noadmin al censo y empezamos la votacion
        user = self.get_or_create_user(1)
        user.is_active = True
        user.save()

        c = Census(voter_id=user.id, voting_id=self.v.id)
        c.save()

        self.v.create_pubkey()
        self.v.start_date = timezone.now()
        self.v.save()

        #Opciones de Chrome
        options = webdriver.ChromeOptions()
        options.headless = True
        self.driver = webdriver.Chrome(options=options)

        super().setUp()            
            
    def tearDown(self): 
        """
        Clean up the test environment after each test method is run.

        This method is called after each test method in the test case.

        :return: None
        """          
        super().tearDown()
        self.driver.quit()

        self.base.tearDown()
    
    def test_testquestionmultipleoptions(self):
        """
        Test the behavior of selecting multiple options in a multiple-choice question booth.

        This test navigates to the booth for a specific voting, logs in as a user, selects multiple options,
        submits the form, and then verifies that the correct number of options is selected and that the form count is as expected.

        :return: None
        """
        self.driver.get(f'{self.live_server_url}/booth/{self.v.id}/')
        self.driver.set_window_size(910, 1016)

        self.driver.find_element(By.ID, "menu-toggle").click()
        
        goto_logging = WebDriverWait(self.driver, 10).until(
        EC.element_to_be_clickable((By.ID, "goto-logging-button"))
            )
        goto_logging.click()

        username = WebDriverWait(self.driver, 10).until(
        EC.element_to_be_clickable((By.ID, "username"))
            )
        username.click()
        
        self.driver.find_element(By.ID, "username").send_keys("user1")
        self.driver.find_element(By.ID, "password").click()
        self.driver.find_element(By.ID, "password").send_keys("qwerty")
        self.driver.find_element(By.ID, "process-login-button").click()

        WebDriverWait(self.driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "form:nth-child(1) > .form-check"))
            )

        self.driver.find_element(By.CSS_SELECTOR, "form:nth-child(1) > .form-check").click()
        self.driver.find_element(By.CSS_SELECTOR, "form:nth-child(2) > .form-check").click()
        self.driver.find_element(By.CSS_SELECTOR, "form:nth-child(3) > .form-check").click()
        
        checkboxes = self.driver.find_elements(By.CSS_SELECTOR, '.form-check input[type="checkbox"]')

        selected_checkboxes = [checkbox for checkbox in checkboxes if checkbox.is_selected()]

        self.driver.find_element(By.CSS_SELECTOR, ".btn-primary").click()

        self.assertTrue(len(selected_checkboxes)==3)
        self.assertTrue(len(self.driver.find_elements(By.CSS_SELECTOR, 'form'))==5)
    


@nottest
class CommentBoothTestCase(StaticLiveServerTestCase):
    """
    Selenium-based test case for the Comment Booth in the voting app.

    This test case covers the behavior of the Comment Booth, including
    the setup, user creation, and interaction with the web interface.

    :ivar base: An instance of BaseTestCase for common test setup and teardown.
    :vartype base: BaseTestCase
    :ivar v: The Voting instance created for testing.
    :vartype v: Voting
    :ivar driver: The Selenium WebDriver instance for browser automation.
    :vartype driver: webdriver.Chrome
    """
    def create_voting(self):
        """
        Create a test voting with a text-type question.

        :return: The created Voting instance.
        :rtype: Voting
        """
        q = Question(desc='test question', type='T')
        q.save()
        v = Voting(name='test voting', question=q)
        v.save()

        a, _ = Auth.objects.get_or_create(url=settings.BASEURL,
                                          defaults={'me': True, 'name': 'test auth'})
        a.save()
        v.auths.add(a)
        return v

    def get_or_create_user(self,pk):
        """
        Get or create a test user.

        :param pk: The primary key for the user.
        :type pk: int
        :return: The User instance.
        :rtype: User
        """
        user, _ = User.objects.get_or_create(pk=pk)
        user.username = 'user{}'.format(pk)
        user.set_password('qwerty')
        user.save()
        return user

    def setUp(self):
        """
        Set up the test environment before each test method is run.

        This method is called before each test method in the test case.

        :return: None
        """
        self.base = BaseTestCase()
        self.base.setUp()

        v = self.create_voting()

        v.question.save()
        self.v = v
        #Añadimos al usuario noadmin al censo y empezamos la votacion
        user = self.get_or_create_user(1)
        user.is_active = True
        user.save()
        c = Census(voter_id=user.id, voting_id=v.id)
        c.save()

        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()

        #Opciones de Chrome
        options = webdriver.ChromeOptions()
        options.headless = True
        self.driver = webdriver.Chrome(options=options)

        super().setUp()            
            
    def tearDown(self): 
        """
        Clean up the test environment after each test method is run.

        This method is called after each test method in the test case.

        :return: None
        """          
        super().tearDown()
        self.driver.quit()

        self.base.tearDown()

    def test_commentquestion(self):
        """
        Test the behavior of submitting a comment in a text-type question booth.

        This test navigates to the booth for a specific voting, logs in as a user, submits a comment,
        and verifies the success alert indicating that the vote has been sent.

        :return: None
        """
        self.driver.get(f'{self.live_server_url}/booth/{self.v.id}/')
        self.driver.set_window_size(910, 1016)

        self.driver.find_element(By.ID, "menu-toggle").click()
        
        goto_logging = WebDriverWait(self.driver, 10).until(
        EC.element_to_be_clickable((By.ID, "goto-logging-button"))
            )
        goto_logging.click()

        username = WebDriverWait(self.driver, 10).until(
        EC.element_to_be_clickable((By.ID, "username"))
            )
        username.click()
        
        self.driver.find_element(By.ID, "username").send_keys("user1")
        self.driver.find_element(By.ID, "password").click()
        self.driver.find_element(By.ID, "password").send_keys("qwerty", Keys.ENTER)

        WebDriverWait(self.driver, 10).until(
        EC.visibility_of_element_located((By.ID, "floatingTextarea2"))
            )

        self.driver.find_element(By.ID, "floatingTextarea2").send_keys("Comentario de prueba")

        self.driver.find_element(By.ID, "send-vote").click()
        
        alert_element = WebDriverWait(self.driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, ".alert"))
            )

        # Verificar que la votación se realizó correctamente
        success_alert = self.driver.page_source
        expected_text = "Congratulations. Your vote has been sent"
        self.assertTrue(expected_text in success_alert, "La alerta de éxito no está presente después de votar")

@nottest
class YesNoBoothTestCase(StaticLiveServerTestCase):
    """
    Selenium-based test case for the Yes/No Question booth in the voting app.

    This test case covers the behavior of the Yes/No Question booth, including
    the setup, user creation, and interaction with the web interface.

    :ivar base: An instance of BaseTestCase for common test setup and teardown.
    :vartype base: BaseTestCase
    :ivar v: The Voting instance created for testing.
    :vartype v: Voting
    :ivar driver: The Selenium WebDriver instance for browser automation.
    :vartype driver: webdriver.Chrome
    """
    def create_voting(self):
        """
        Create a test voting with a Yes/No type question.

        :return: The created Voting instance.
        :rtype: Voting
        """
        q = Question(desc='test question', type='Y')
        q.save()
        v = Voting(name='test voting', question=q)
        v.save()

        a, _ = Auth.objects.get_or_create(url=settings.BASEURL,
                                          defaults={'me': True, 'name': 'test auth'})
        a.save()
        v.auths.add(a)
        return v

    def get_or_create_user(self,pk):
        """
        Get or create a test user.

        :param pk: The primary key for the user.
        :type pk: int
        :return: The User instance.
        :rtype: User
        """
        user, _ = User.objects.get_or_create(pk=pk)
        user.username = 'user{}'.format(pk)
        user.set_password('qwerty')
        user.save()
        return user
    
    def setUp(self):
        """
        Set up the test environment before each test method is run.

        This method is called before each test method in the test case.

        :return: None
        """
        self.base = BaseTestCase()
        self.base.setUp()

        v = self.create_voting()
        v.question.type = 'Y'
        v.question.save()
        self.v = v
        #Añadimos al usuario noadmin al censo y empezamos la votacion
        user = self.get_or_create_user(1)
        user.is_active = True
        user.save()
        c = Census(voter_id=user.id, voting_id=v.id)
        c.save()

        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()
    
        #Opciones de Chrome
        options = webdriver.ChromeOptions()
        options.headless = True
        self.driver = webdriver.Chrome(options=options)

        super().setUp()            
            
    def tearDown(self):     
        """
        Clean up the test environment after each test method is run.

        This method is called after each test method in the test case.

        :return: None
        """      
        super().tearDown()
        self.driver.quit()

        self.base.tearDown()  
    
    def test_testquestionyesno(self):
        """
        Test the behavior of submitting a Yes/No response in a Yes/No type question booth.

        This test navigates to the booth for a specific voting, logs in as a user, submits a Yes response,
        and verifies the success alert indicating that the vote has been sent.

        :return: None
        """
        self.driver.get(f'{self.live_server_url}/booth/{self.v.id}/')
        self.driver.set_window_size(910, 1016)

        self.driver.find_element(By.ID, "menu-toggle").click()
        
        goto_logging = WebDriverWait(self.driver, 10).until(
        EC.element_to_be_clickable((By.ID, "goto-logging-button"))
            )
        goto_logging.click()

        username = WebDriverWait(self.driver, 10).until(
        EC.element_to_be_clickable((By.ID, "username"))
            )
        username.click()
        
        self.driver.find_element(By.ID, "username").send_keys("user1")
        self.driver.find_element(By.ID, "password").click()
        self.driver.find_element(By.ID, "password").send_keys("qwerty", Keys.ENTER)
        
        yes_button = WebDriverWait(self.driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn-success"))
            )
        yes_button.click()

        alert_element = WebDriverWait(self.driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, ".alert"))
            )

        # Verificar que la votación se realizó correctamente
        success_alert = self.driver.page_source
        expected_text = "Congratulations. Your vote has been sent"
        self.assertTrue(expected_text in success_alert, "La alerta de éxito no está presente después de votar")
  

@nottest
class PreferenceBoothTest(StaticLiveServerTestCase):
    """
    Selenium-based test case for the Preference Question booth in the voting app.

    This test case covers the behavior of the Preference Question booth, including
    the setup, user creation, and interaction with the web interface.

    :ivar base: An instance of BaseTestCase for common test setup and teardown.
    :vartype base: BaseTestCase
    :ivar v: The Voting instance created for testing.
    :vartype v: Voting
    :ivar driver: The Selenium WebDriver instance for browser automation.
    :vartype driver: webdriver.Chrome
    """
    def create_voting(self):
        """
        Create a test voting with a Preference type question.

        :return: The created Voting instance.
        :rtype: Voting
        """
        q = Question(desc='test question', type='R')
        q.save()
        opt1 = QuestionOptionRanked(question=q, option='Test 1', number=1)
        opt2 = QuestionOptionRanked(question=q, option='Test 2', number=2)
        opt1.save()
        opt2.save()
        v = Voting(name='test voting', question=q)
        v.save()

        a, _ = Auth.objects.get_or_create(url=settings.BASEURL,
                                          defaults={'me': True, 'name': 'test auth'})
        a.save()
        v.auths.add(a)
        return v

    def get_or_create_user(self,pk):
        """
        Get or create a test user.

        :param pk: The primary key for the user.
        :type pk: int
        :return: The User instance.
        :rtype: User
        """
        user, _ = User.objects.get_or_create(pk=pk)
        user.username = f'user: {pk}'
        user.set_password('qwerty')
        user.save()
        return user

    def setUp(self):
        """
        Set up the test environment before each test method is run.

        This method is called before each test method in the test case.

        :return: None
        """
        self.base = BaseTestCase()
        self.base.setUp()

        v = self.create_voting()
        v.question.type = 'R'
        v.question.save()
        self.v = v
        #Añadimos al usuario noadmin al censo y empezamos la votacion
        user = self.get_or_create_user(1)
        user.is_active = True
        user.save()
        c = Census(voter_id=user.id, voting_id=v.id)
        c.save()

        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()
    
        #Opciones de Chrome
        options = webdriver.ChromeOptions()
        options.headless = True
        self.driver = webdriver.Chrome(options=options)

        super().setUp()            
            
    def tearDown(self):   
        """
        Clean up the test environment after each test method is run.

        This method is called after each test method in the test case.

        :return: None
        """        
        super().tearDown()
        self.driver.quit()

        self.base.tearDown()
    
    def test_question_preference(self):
        """
        Test the behavior of submitting a preference response in a Preference type question booth.

        This test navigates to the booth for a specific voting, logs in as a user, submits a preference response,
        and verifies the success alert indicating that the vote has been sent.

        :return: None
        """
        self.driver.get(f'{self.live_server_url}/booth/{self.v.id}/')
        self.driver.set_window_size(910, 1016)

        time.sleep(1)
        self.driver.find_element(By.CSS_SELECTOR, ".navbar-toggler-icon").click()
        time.sleep(1)
        self.driver.find_element(By.CSS_SELECTOR, ".btn-secondary").click()
        time.sleep(1)
        self.driver.find_element(By.ID, "username").send_keys("user1")
        time.sleep(1)

        self.driver.find_element(By.ID, "password").send_keys("qwerty")
        time.sleep(1)

        self.driver.find_element(By.CSS_SELECTOR, ".btn-primary").click()
        time.sleep(1)

        # Realizar la votación votando Sí
        self.driver.find_element(By.CSS_SELECTOR,  "form:nth-child(1) .form-ranked-input").send_keys("1")
        self.driver.find_element(By.CSS_SELECTOR,  "form:nth-child(1) .form-ranked-input").click()
        time.sleep(1)
        self.driver.find_element(By.CSS_SELECTOR,  "form:nth-child(2) .form-ranked-input").send_keys("1")
        self.driver.find_element(By.CSS_SELECTOR,  "form:nth-child(2) .form-ranked-input").click()
        time.sleep(1)
        self.driver.find_element(By.CSS_SELECTOR,  "form:nth-child(2) .form-ranked-input").send_keys("2")
        self.driver.find_element(By.CSS_SELECTOR,  "form:nth-child(2) .form-ranked-input").click()
        time.sleep(1)

        self.driver.find_element(By.CSS_SELECTOR, ".btn-primary").click()

        # Verificar que la votación se realizó correctamente
        success_alert = self.driver.page_source
        expected_text = "Congratulations. Your vote has been sent"
        self.assertTrue(expected_text in success_alert, "La alerta de éxito no está presente después de votar")
    
    def test_preference_booth_same_preference(self):
        """
        Test the behavior when trying to submit a preference with repeated rankings.

        This test navigates to the booth for a specific voting, logs in as a user, tries to submit a preference with repeated rankings,
        and verifies the error alert indicating that preferences cannot be repeated.

        :return: None
        """
        self.driver.get(f'{self.live_server_url}/booth/{self.v.id}/')
        self.driver.set_window_size(910, 1016)

        time.sleep(1)
        self.driver.find_element(By.CSS_SELECTOR, ".navbar-toggler-icon").click()
        time.sleep(1)
        self.driver.find_element(By.CSS_SELECTOR, ".btn-secondary").click()
        time.sleep(1)
        self.driver.find_element(By.ID, "username").send_keys("noadmin")
        time.sleep(1)

        self.driver.find_element(By.ID, "password").send_keys("qwerty")
        time.sleep(1)

        self.driver.find_element(By.CSS_SELECTOR, ".btn-primary").click()
        time.sleep(1)

        self.driver.find_element(By.CSS_SELECTOR,  "form:nth-child(1) .form-ranked-input").send_keys("1")
        self.driver.find_element(By.CSS_SELECTOR,  "form:nth-child(1) .form-ranked-input").click()
        time.sleep(1)
        self.driver.find_element(By.CSS_SELECTOR,  "form:nth-child(2) .form-ranked-input").send_keys("1")
        self.driver.find_element(By.CSS_SELECTOR,  "form:nth-child(2) .form-ranked-input").click()
        time.sleep(1)

        self.driver.find_element(By.CSS_SELECTOR, ".btn-primary").click()

        # Verificar que la votación se realizó correctamente
        canceled_alert = self.driver.page_source
        expected_text = "Error: No puede haber preferencias repetidas entre opciones"
        self.assertTrue(expected_text in canceled_alert, "La alerta de éxito no está presente después de votar")

    def test_preference_booth_no_fullfile_all_preferences(self):
        """
        Test the behavior when trying to submit a preference without providing a complete set of rankings.

        This test navigates to the booth for a specific voting, logs in as a user, tries to submit a preference without providing a complete set of rankings,
        and verifies the error alert indicating that all preferences must be chosen.

        :return: None
        """
        self.driver.get(f'{self.live_server_url}/booth/{self.v.id}/')
        self.driver.set_window_size(910, 1016)

        time.sleep(1)
        self.driver.find_element(By.CSS_SELECTOR, ".navbar-toggler-icon").click()
        time.sleep(1)
        self.driver.find_element(By.CSS_SELECTOR, ".btn-secondary").click()
        time.sleep(1)
        self.driver.find_element(By.ID, "username").send_keys("noadmin")
        time.sleep(1)

        self.driver.find_element(By.ID, "password").send_keys("qwerty")
        time.sleep(1)

        self.driver.find_element(By.CSS_SELECTOR, ".btn-primary").click()
        time.sleep(1)

        self.driver.find_element(By.CSS_SELECTOR,  "form:nth-child(1) .form-ranked-input").send_keys("1")
        self.driver.find_element(By.CSS_SELECTOR,  "form:nth-child(1) .form-ranked-input").click()
        time.sleep(1)

        self.driver.find_element(By.CSS_SELECTOR, ".btn-primary").click()

        # Verificar que la votación se realizó correctamente
        canceled_alert = self.driver.page_source
        expected_text = "Error: Se tienen que escoger la preferencia de todas las opciones"
        self.assertTrue(expected_text in canceled_alert, "La alerta de éxito no está presente después de votar")