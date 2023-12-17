from rest_framework.test import APIClient
from rest_framework.test import APITestCase

from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from base.tests import BaseTestCase 
from selenium import webdriver
from selenium.webdriver.common.by import By

from base import mods


class TestRegisterPositive(StaticLiveServerTestCase):
    """
    Test case for positive user registration scenarios.

    Inherits from StaticLiveServerTestCase to test views using a live server.

    Methods:
    - setUp: Set up the test environment before each test case.
    - tearDown: Tear down the test environment after each test case.
    - testregisterpositive: Test positive user registration.
    """

    def setUp(self):
        """
        Set up the test environment before each test case.

        - Creates a BaseTestCase instance.
        - Configures a headless Chrome browser for testing.
        """
        self.base = BaseTestCase()
        self.base.setUp()

        options = webdriver.ChromeOptions()
        options.headless = True 
        self.cleaner = webdriver.Chrome(options=options)

        super().setUp()            
            
    def tearDown(self):
        """
        Tear down the test environment after each test case.

        - Quits the Chrome browser.
        - Calls the tearDown method of the BaseTestCase instance.
        """           
        super().tearDown()
        self.cleaner.quit()
        self.base.tearDown()
  
    def testregisterpositive(self):
        """
        Test positive user registration.

        - Accesses the registration view.
        - Fills in valid user registration information.
        - Submits the registration form.
        - Asserts that the user is redirected to the home page.
        """
        self.cleaner.get(self.live_server_url+"/authentication/register-view/")
        
        self.cleaner.find_element(By.ID, "id_username").click()
        self.cleaner.find_element(By.ID, "id_username").send_keys("testuser")
        self.cleaner.find_element(By.ID, "id_password1").click()
        self.cleaner.find_element(By.ID, "id_password1").send_keys("testpasword123")
        self.cleaner.find_element(By.ID, "id_password2").click()
        self.cleaner.find_element(By.ID, "id_password2").send_keys("testpasword123")
        self.cleaner.find_element(By.ID, "id_email").click()
        self.cleaner.find_element(By.ID, "id_email").send_keys("test@test.com")
        self.cleaner.find_element(By.ID, "id_first_name").click()
        self.cleaner.find_element(By.ID, "id_first_name").send_keys("Alex")
        self.cleaner.find_element(By.ID, "id_last_name").click()
        self.cleaner.find_element(By.ID, "id_last_name").send_keys("Smith")
        self.cleaner.find_element(By.CSS_SELECTOR, ".btn").click()

        self.assertTrue(self.cleaner.current_url == self.live_server_url+"/")

class TestRegisterNegative(StaticLiveServerTestCase):
    """
    Test case for negative user registration scenarios.

    Inherits from StaticLiveServerTestCase to test views using a live server.

    Methods:
    - setUp: Set up the test environment before each test case.
    - tearDown: Tear down the test environment after each test case.
    - testregisternegativewrongpassword: Test user registration with mismatched passwords.
    - testregisternegativelongusername: Test user registration with a too-long username.
    - testregisternegativeusername: Test user registration with an already taken username.
    - testregisternegativepatternusername: Test user registration with an invalid username pattern.
    - testregisternegativeemail: Test user registration with an already taken email.
    - testregisternegativeemail: Test user registration with an invalid email.
    - testregisternegativeemail: Test user registration with a short password.
    - testregisternegativecommonpass: Test user registration with a common password.
    - testregisternegativesimilarpass: Test user registration with a password similar to the username.
    - testregisternegativenumericpass: Test user registration with a numeric password.
    """

    def setUp(self):
        """
        Set up the test environment before each test case.

        - Creates a BaseTestCase instance.
        - Configures a headless Chrome browser for testing.
        - Sets up a mock API client.
        - Creates a test user in the database.
        """
        self.base = BaseTestCase()
        self.base.setUp()

        self.client = APIClient()
        mods.mock_query(self.client)
        u = User(username='prueba1')
        u.set_password('contrasenia1')
        u.email = "test@gmail.com"
        u.save()

        options = webdriver.ChromeOptions()
        options.headless = True
        self.cleaner = webdriver.Chrome(options=options)

        super().setUp()            
            
    def tearDown(self):
        """
        Tear down the test environment after each test case.

        - Quits the Chrome browser.
        - Calls the tearDown method of the BaseTestCase instance.
        """           
        super().tearDown()
        self.cleaner.quit()
        self.base.tearDown()
  
    def testregisternegativewrongpassword(self):
        """
        Test user registration with mismatched passwords.

        - Accesses the registration view.
        - Fills in registration form with mismatched passwords.
        - Submits the form.
        - Asserts that the user stays on the registration view and sees an alert.
        """
        self.cleaner.get(self.live_server_url+"/authentication/register-view/")
        
        self.cleaner.find_element(By.ID, "id_username").click()
        self.cleaner.find_element(By.ID, "id_username").send_keys("testuser")
        self.cleaner.find_element(By.ID, "id_password1").click()
        self.cleaner.find_element(By.ID, "id_password1").send_keys("testpasword123")
        self.cleaner.find_element(By.ID, "id_password2").click()
        self.cleaner.find_element(By.ID, "id_password2").send_keys("testpasword12")
        self.cleaner.find_element(By.ID, "id_email").click()
        self.cleaner.find_element(By.ID, "id_email").send_keys("test@test.com")
        self.cleaner.find_element(By.ID, "id_first_name").click()
        self.cleaner.find_element(By.ID, "id_first_name").send_keys("Alex")
        self.cleaner.find_element(By.ID, "id_last_name").click()
        self.cleaner.find_element(By.ID, "id_last_name").send_keys("Smith")
        self.cleaner.find_element(By.CSS_SELECTOR, ".btn").click()

        self.assertTrue(self.cleaner.current_url == self.live_server_url+"/authentication/register-view/")
        self.assertTrue( self.cleaner.find_element(By.CSS_SELECTOR, ".alert").text == "Passwords must be the same")

    def testregisternegativelongusername(self):
        """
        Test user registration with a too-long username.

        - Accesses the registration view.
        - Fills in the registration form with a too-long username.
        - Submits the form.
        - Asserts that the user stays on the registration view and sees an alert.

        :return: None
        """
        self.cleaner.get(self.live_server_url+"/authentication/register-view/")
        
        self.cleaner.find_element(By.ID, "id_username").click()
        self.cleaner.find_element(By.ID, "id_username").send_keys("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
        self.cleaner.find_element(By.ID, "id_password1").click()
        self.cleaner.find_element(By.ID, "id_password1").send_keys("testpasword123")
        self.cleaner.find_element(By.ID, "id_password2").click()
        self.cleaner.find_element(By.ID, "id_password2").send_keys("testpasword123")
        self.cleaner.find_element(By.ID, "id_email").click()
        self.cleaner.find_element(By.ID, "id_email").send_keys("test1@test.com")
        self.cleaner.find_element(By.ID, "id_first_name").click()
        self.cleaner.find_element(By.ID, "id_first_name").send_keys("Alex")
        self.cleaner.find_element(By.ID, "id_last_name").click()
        self.cleaner.find_element(By.ID, "id_last_name").send_keys("Smith")
        self.cleaner.find_element(By.CSS_SELECTOR, ".btn").click()

        self.assertTrue(self.cleaner.current_url == self.live_server_url+"/authentication/register-view/")
        self.assertTrue( self.cleaner.find_element(By.CSS_SELECTOR, ".alert").text == "This username is larger than 150 characters")

    def testregisternegativeusername(self):
        """
        Test user registration with an already taken username.

        - Accesses the registration view.
        - Fills in the registration form with an already taken username.
        - Submits the form.
        - Asserts that the user stays on the registration view and sees an alert.

        :return: None
        """
        self.cleaner.get(self.live_server_url+"/authentication/register-view/")
        
        self.cleaner.find_element(By.ID, "id_username").click()
        self.cleaner.find_element(By.ID, "id_username").send_keys("prueba1")
        self.cleaner.find_element(By.ID, "id_password1").click()
        self.cleaner.find_element(By.ID, "id_password1").send_keys("testpasword123")
        self.cleaner.find_element(By.ID, "id_password2").click()
        self.cleaner.find_element(By.ID, "id_password2").send_keys("testpasword123")
        self.cleaner.find_element(By.ID, "id_email").click()
        self.cleaner.find_element(By.ID, "id_email").send_keys("test2@test.com")
        self.cleaner.find_element(By.ID, "id_first_name").click()
        self.cleaner.find_element(By.ID, "id_first_name").send_keys("Alex")
        self.cleaner.find_element(By.ID, "id_last_name").click()
        self.cleaner.find_element(By.ID, "id_last_name").send_keys("Smith")
        self.cleaner.find_element(By.CSS_SELECTOR, ".btn").click()

        self.assertTrue(self.cleaner.current_url == self.live_server_url+"/authentication/register-view/")
        self.assertTrue( self.cleaner.find_element(By.CSS_SELECTOR, ".alert").text == "This username has already taken")

    def testregisternegativepatternusername(self):
        """
        Test user registration with an invalid username pattern.

        - Accesses the registration view.
        - Fills in the registration form with an invalid username pattern.
        - Submits the form.
        - Asserts that the user stays on the registration view and sees an alert.

        :return: None
        """
        self.cleaner.get(self.live_server_url+"/authentication/register-view/")
        
        self.cleaner.find_element(By.ID, "id_username").click()
        self.cleaner.find_element(By.ID, "id_username").send_keys("test$%&user")
        self.cleaner.find_element(By.ID, "id_password1").click()
        self.cleaner.find_element(By.ID, "id_password1").send_keys("testpasword123")
        self.cleaner.find_element(By.ID, "id_password2").click()
        self.cleaner.find_element(By.ID, "id_password2").send_keys("testpasword123")
        self.cleaner.find_element(By.ID, "id_email").click()
        self.cleaner.find_element(By.ID, "id_email").send_keys("test4@test.com")
        self.cleaner.find_element(By.ID, "id_first_name").click()
        self.cleaner.find_element(By.ID, "id_first_name").send_keys("Alex")
        self.cleaner.find_element(By.ID, "id_last_name").click()
        self.cleaner.find_element(By.ID, "id_last_name").send_keys("Smith")
        self.cleaner.find_element(By.CSS_SELECTOR, ".btn").click()

        self.assertTrue(self.cleaner.current_url == self.live_server_url+"/authentication/register-view/")
        self.assertTrue( self.cleaner.find_element(By.CSS_SELECTOR, ".alert").text == "This username not match with the pattern")

    def testregisternegativeemail(self):
        self.cleaner.get(self.live_server_url+"/authentication/register-view/")
        
        self.cleaner.find_element(By.ID, "id_username").click()
        self.cleaner.find_element(By.ID, "id_username").send_keys("testuser5")
        self.cleaner.find_element(By.ID, "id_password1").click()
        self.cleaner.find_element(By.ID, "id_password1").send_keys("testpasword123")
        self.cleaner.find_element(By.ID, "id_password2").click()
        self.cleaner.find_element(By.ID, "id_password2").send_keys("testpasword123")
        self.cleaner.find_element(By.ID, "id_email").click()
        self.cleaner.find_element(By.ID, "id_email").send_keys("test@gmail.com")
        self.cleaner.find_element(By.ID, "id_first_name").click()
        self.cleaner.find_element(By.ID, "id_first_name").send_keys("Alex")
        self.cleaner.find_element(By.ID, "id_last_name").click()
        self.cleaner.find_element(By.ID, "id_last_name").send_keys("Smith")
        self.cleaner.find_element(By.CSS_SELECTOR, ".btn").click()

        self.assertTrue(self.cleaner.current_url == self.live_server_url+"/authentication/register-view/")
        self.assertTrue( self.cleaner.find_element(By.CSS_SELECTOR, ".alert").text == "This email has already taken")
    
    def testregisternegativeemail(self):
        """
        Test user registration with an already taken email.

        - Accesses the registration view.
        - Fills in the registration form with an already taken email.
        - Submits the form.
        - Asserts that the user stays on the registration view and sees an alert.

        :return: None
        """
        self.cleaner.get(self.live_server_url+"/authentication/register-view/")
        
        self.cleaner.find_element(By.ID, "id_username").click()
        self.cleaner.find_element(By.ID, "id_username").send_keys("testuser5")
        self.cleaner.find_element(By.ID, "id_password1").click()
        self.cleaner.find_element(By.ID, "id_password1").send_keys("testpasword123")
        self.cleaner.find_element(By.ID, "id_password2").click()
        self.cleaner.find_element(By.ID, "id_password2").send_keys("testpasword123")
        self.cleaner.find_element(By.ID, "id_email").click()
        self.cleaner.find_element(By.ID, "id_email").send_keys("test@gmail.com")
        self.cleaner.find_element(By.ID, "id_first_name").click()
        self.cleaner.find_element(By.ID, "id_first_name").send_keys("Alex")
        self.cleaner.find_element(By.ID, "id_last_name").click()
        self.cleaner.find_element(By.ID, "id_last_name").send_keys("Smith")
        self.cleaner.find_element(By.CSS_SELECTOR, ".btn").click()

        self.assertTrue(self.cleaner.current_url == self.live_server_url+"/authentication/register-view/")
        self.assertTrue( self.cleaner.find_element(By.CSS_SELECTOR, ".alert").text == "This email has already taken")

    def testregisternegativeemail(self):
        """
        Test user registration with a short password.

        - Accesses the registration view.
        - Fills in the registration form with a short password.
        - Submits the form.
        - Asserts that the user stays on the registration view and sees an alert.

        :return: None
        """
        self.cleaner.get(self.live_server_url+"/authentication/register-view/")
        
        self.cleaner.find_element(By.ID, "id_username").click()
        self.cleaner.find_element(By.ID, "id_username").send_keys("testuser6")
        self.cleaner.find_element(By.ID, "id_password1").click()
        self.cleaner.find_element(By.ID, "id_password1").send_keys("test")
        self.cleaner.find_element(By.ID, "id_password2").click()
        self.cleaner.find_element(By.ID, "id_password2").send_keys("test")
        self.cleaner.find_element(By.ID, "id_email").click()
        self.cleaner.find_element(By.ID, "id_email").send_keys("test6@test.com")
        self.cleaner.find_element(By.ID, "id_first_name").click()
        self.cleaner.find_element(By.ID, "id_first_name").send_keys("Alex")
        self.cleaner.find_element(By.ID, "id_last_name").click()
        self.cleaner.find_element(By.ID, "id_last_name").send_keys("Smith")
        self.cleaner.find_element(By.CSS_SELECTOR, ".btn").click()

        self.assertTrue(self.cleaner.current_url == self.live_server_url+"/authentication/register-view/")
        self.assertTrue( self.cleaner.find_element(By.CSS_SELECTOR, ".alert").text == "This password must contain at least 8 characters")

    def testregisternegativecommonpass(self):
        """
        Test user registration with a common password.

        - Accesses the registration view.
        - Fills in the registration form with a common password.
        - Submits the form.
        - Asserts that the user stays on the registration view and sees an alert.

        :return: None
        """
        self.cleaner.get(self.live_server_url+"/authentication/register-view/")
        
        self.cleaner.find_element(By.ID, "id_username").click()
        self.cleaner.find_element(By.ID, "id_username").send_keys("testuser7")
        self.cleaner.find_element(By.ID, "id_password1").click()
        self.cleaner.find_element(By.ID, "id_password1").send_keys("12345678")
        self.cleaner.find_element(By.ID, "id_password2").click()
        self.cleaner.find_element(By.ID, "id_password2").send_keys("12345678")
        self.cleaner.find_element(By.ID, "id_email").click()
        self.cleaner.find_element(By.ID, "id_email").send_keys("test7@test.com")
        self.cleaner.find_element(By.ID, "id_first_name").click()
        self.cleaner.find_element(By.ID, "id_first_name").send_keys("Alex")
        self.cleaner.find_element(By.ID, "id_last_name").click()
        self.cleaner.find_element(By.ID, "id_last_name").send_keys("Smith")
        self.cleaner.find_element(By.CSS_SELECTOR, ".btn").click()

        self.assertTrue(self.cleaner.current_url == self.live_server_url+"/authentication/register-view/")
        self.assertTrue( self.cleaner.find_element(By.CSS_SELECTOR, ".alert").text == "This password is a common password")

    def testregisternegativesimilarpass(self):
        """
        Test user registration with a password similar to the username.

        - Accesses the registration view.
        - Fills in the registration form with a password similar to the username.
        - Submits the form.
        - Asserts that the user stays on the registration view and sees an alert.

        :return: None
        """
        self.cleaner.get(self.live_server_url+"/authentication/register-view/")
        
        self.cleaner.find_element(By.ID, "id_username").click()
        self.cleaner.find_element(By.ID, "id_username").send_keys("testuser8")
        self.cleaner.find_element(By.ID, "id_password1").click()
        self.cleaner.find_element(By.ID, "id_password1").send_keys("testuser8")
        self.cleaner.find_element(By.ID, "id_password2").click()
        self.cleaner.find_element(By.ID, "id_password2").send_keys("testuser8")
        self.cleaner.find_element(By.ID, "id_email").click()
        self.cleaner.find_element(By.ID, "id_email").send_keys("test8@test.com")
        self.cleaner.find_element(By.ID, "id_first_name").click()
        self.cleaner.find_element(By.ID, "id_first_name").send_keys("Alex")
        self.cleaner.find_element(By.ID, "id_last_name").click()
        self.cleaner.find_element(By.ID, "id_last_name").send_keys("Smith")
        self.cleaner.find_element(By.CSS_SELECTOR, ".btn").click()

        self.assertTrue(self.cleaner.current_url == self.live_server_url+"/authentication/register-view/")
        self.assertTrue( self.cleaner.find_element(By.CSS_SELECTOR, ".alert").text == "This password is too similar to your personal data")

    def testregisternegativenumericpass(self):
        """
        Test user registration with a numeric password.

        - Accesses the registration view.
        - Fills in the registration form with a numeric password.
        - Submits the form.
        - Asserts that the user stays on the registration view and sees an alert.

        :return: None
        """
        self.cleaner.get(self.live_server_url+"/authentication/register-view/")
        
        self.cleaner.find_element(By.ID, "id_username").click()
        self.cleaner.find_element(By.ID, "id_username").send_keys("testuser9")
        self.cleaner.find_element(By.ID, "id_password1").click()
        self.cleaner.find_element(By.ID, "id_password1").send_keys("638372334453")
        self.cleaner.find_element(By.ID, "id_password2").click()
        self.cleaner.find_element(By.ID, "id_password2").send_keys("638372334453")
        self.cleaner.find_element(By.ID, "id_email").click()
        self.cleaner.find_element(By.ID, "id_email").send_keys("test9@test.com")
        self.cleaner.find_element(By.ID, "id_first_name").click()
        self.cleaner.find_element(By.ID, "id_first_name").send_keys("Alex")
        self.cleaner.find_element(By.ID, "id_last_name").click()
        self.cleaner.find_element(By.ID, "id_last_name").send_keys("Smith")
        self.cleaner.find_element(By.CSS_SELECTOR, ".btn").click()

        self.assertTrue(self.cleaner.current_url == self.live_server_url+"/authentication/register-view/")
        self.assertTrue( self.cleaner.find_element(By.CSS_SELECTOR, ".alert").text == "This password is numeric")


class TestLoginPositive(StaticLiveServerTestCase):
    """
    Test case for positive user login scenarios.

    Inherits from StaticLiveServerTestCase to test views using a live server.

    Methods:
    - setUp: Set up the test environment before each test case.
    - tearDown: Tear down the test environment after each test case.
    - testloginpositive: Test positive user login.
    """

    def setUp(self):
        """
        Set up the test environment before each test case.

        - Creates a BaseTestCase instance.
        - Configures a headless Chrome browser for testing.
        """
        self.base = BaseTestCase()
        self.base.setUp()

        options = webdriver.ChromeOptions()
        options.headless = True
        self.cleaner = webdriver.Chrome(options=options)

        super().setUp()            
            
    def tearDown(self):
        """
        Tear down the test environment after each test case.

        - Quits the Chrome browser.
        - Calls the tearDown method of the BaseTestCase instance.
        """
           
        super().tearDown()
        self.cleaner.quit()
        self.base.tearDown()
  
    def testloginpositive(self):
        """
        Test positive user login.

        - Accesses the registration view.
        - Registers a new user.
        - Logs in with the registered user credentials.
        - Asserts that the user is redirected to the home page.
        """
        self.cleaner.get(self.live_server_url+"/authentication/register-view/")
        
        self.cleaner.find_element(By.ID, "id_username").click()
        self.cleaner.find_element(By.ID, "id_username").send_keys("testlogin")
        self.cleaner.find_element(By.ID, "id_password1").click()
        self.cleaner.find_element(By.ID, "id_password1").send_keys("login1234")
        self.cleaner.find_element(By.ID, "id_password2").click()
        self.cleaner.find_element(By.ID, "id_password2").send_keys("login1234")
        self.cleaner.find_element(By.ID, "id_email").click()
        self.cleaner.find_element(By.ID, "id_email").send_keys("login@test.com")
        self.cleaner.find_element(By.ID, "id_first_name").click()
        self.cleaner.find_element(By.ID, "id_first_name").send_keys("Alex")
        self.cleaner.find_element(By.ID, "id_last_name").click()
        self.cleaner.find_element(By.ID, "id_last_name").send_keys("Smith")
        self.cleaner.find_element(By.CSS_SELECTOR, ".btn").click()

        self.assertTrue(self.cleaner.current_url == self.live_server_url+"/")

        self.cleaner.get(self.live_server_url+"/authentication/login-view/")

        self.cleaner.find_element(By.ID, "id_username").click()
        self.cleaner.find_element(By.ID, "id_username").send_keys("testlogin")
        self.cleaner.find_element(By.ID, "id_password1").click()
        self.cleaner.find_element(By.ID, "id_password1").send_keys("login1234")
        self.cleaner.find_element(By.CSS_SELECTOR, ".btn").click()

        self.assertTrue(self.cleaner.current_url == self.live_server_url+"/")

class TestLoginNegative(StaticLiveServerTestCase):
    """
    Test case for negative user login scenarios.

    Inherits from StaticLiveServerTestCase to test views using a live server.

    Methods:
    - setUp: Set up the test environment before each test case.
    - tearDown: Tear down the test environment after each test case.
    - testloginnegative: Test negative user login.
    """

    def setUp(self):
        """
        Set up the test environment before each test case.

        - Creates a BaseTestCase instance.
        - Configures a headless Chrome browser for testing.
        """
        self.base = BaseTestCase()
        self.base.setUp()

        options = webdriver.ChromeOptions()
        options.headless = True
        self.cleaner = webdriver.Chrome(options=options)

        super().setUp()            
            
    def tearDown(self):
        """
        Tear down the test environment after each test case.

        - Quits the Chrome browser.
        - Calls the tearDown method of the BaseTestCase instance.
        """           
        super().tearDown()
        self.cleaner.quit()
        self.base.tearDown()
  
    def testloginnegative(self):
        """
        Test negative user login.

        - Accesses the login view.
        - Attempts to log in with invalid credentials.
        - Asserts that the user stays on the login view and sees an alert.
        """
        self.cleaner.get(self.live_server_url+"/authentication/login-view/")
        
        self.cleaner.find_element(By.ID, "id_username").click()
        self.cleaner.find_element(By.ID, "id_username").send_keys("testnegative")
        self.cleaner.find_element(By.ID, "id_password1").click()
        self.cleaner.find_element(By.ID, "id_password1").send_keys("testnegative123")
        self.cleaner.find_element(By.CSS_SELECTOR, ".btn").click()

        
        self.assertTrue(self.cleaner.current_url == self.live_server_url+"/authentication/login-view/")
        self.assertTrue( self.cleaner.find_element(By.CSS_SELECTOR, ".alert").text == "This username or password do not exist")
        