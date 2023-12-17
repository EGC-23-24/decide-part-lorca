from rest_framework.test import APIClient
from rest_framework.test import APITestCase

from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from base.tests import BaseTestCase 
from selenium import webdriver
from selenium.webdriver.common.by import By

from base import mods


class AuthTestCase(APITestCase):
    """
    Test case for authentication-related functionality.

    Inherits from APITestCase to provide utility functions for making API requests.
    """
    def setUp(self):
        """
        Set up the test environment.

        Creates a test client, mocks a database query, and creates two users for testing.
        """
        self.client = APIClient()
        mods.mock_query(self.client)
        u = User(username='voter1')
        u.set_password('123')
        u.save()

        u2 = User(username='admin')
        u2.set_password('admin')
        u2.is_superuser = True
        u2.save()

    def tearDown(self):
        """
        Tear down the test environment.

        Resets the test client to None.
        """
        self.client = None

    def test_login(self):
        """
        Test the login functionality.

        Attempts to log in with valid credentials and checks for the presence of a token.

        :return: None
        """
        data = {'username': 'voter1', 'password': '123'}
        response = self.client.post('/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 200)

        token = response.json()
        self.assertTrue(token.get('token'))

    def test_login_fail(self):
        """
        Test login failure with incorrect password.

        Attempts to log in with incorrect credentials and expects a 400 status code.

        :return: None
        """
        data = {'username': 'voter1', 'password': '321'}
        response = self.client.post('/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_getuser(self):
        """
        Test retrieving user information after successful login.

        Logs in a user, retrieves the user information, and checks if the received data is correct.

        :return: None
        """
        data = {'username': 'voter1', 'password': '123'}
        response = self.client.post('/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 200)
        token = response.json()

        response = self.client.post('/authentication/getuser/', token, format='json')
        self.assertEqual(response.status_code, 200)

        user = response.json()
        self.assertEqual(user['id'], 1)
        self.assertEqual(user['username'], 'voter1')

    def test_getuser_invented_token(self):
        """
        Test retrieving user information with an invented token.

        Tries to retrieve user information with a token that does not exist and expects a 404 status code.

        :return: None
        """
        token = {'token': 'invented'}
        response = self.client.post('/authentication/getuser/', token, format='json')
        self.assertEqual(response.status_code, 404)

    def test_getuser_invalid_token(self):
        """
        Test retrieving user information with an invalid token.

        Logs in a user, logs them out, and then attempts to retrieve user information with the invalidated token.
        Expects a 404 status code.

        :return: None
        """
        data = {'username': 'voter1', 'password': '123'}
        response = self.client.post('/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Token.objects.filter(user__username='voter1').count(), 1)

        token = response.json()
        self.assertTrue(token.get('token'))

        response = self.client.post('/authentication/logout/', token, format='json')
        self.assertEqual(response.status_code, 200)

        response = self.client.post('/authentication/getuser/', token, format='json')
        self.assertEqual(response.status_code, 404)

    def test_logout(self):
        """
        Test user logout.

        Logs in a user, logs them out, and checks if the corresponding token is removed.

        :return: None
        """
        data = {'username': 'voter1', 'password': '123'}
        response = self.client.post('/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Token.objects.filter(user__username='voter1').count(), 1)

        token = response.json()
        self.assertTrue(token.get('token'))

        response = self.client.post('/authentication/logout/', token, format='json')
        self.assertEqual(response.status_code, 200)

        self.assertEqual(Token.objects.filter(user__username='voter1').count(), 0)

    def test_register_bad_permissions(self):
        """
        Test user registration with insufficient permissions.

        Logs in a user with insufficient permissions, attempts to register a new user,
        and expects a 401 status code.

        :return: None
        """
        data = {'username': 'voter1', 'password': '123'}
        response = self.client.post('/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 200)
        token = response.json()

        token.update({'username': 'user1'})
        response = self.client.post('/authentication/register/', token, format='json')
        self.assertEqual(response.status_code, 401)

    def test_register_bad_request(self):
        """
        Test user registration with a bad request.

        Logs in as an admin, attempts to register a new user with incomplete data,
        and expects a 400 status code.

        :return: None
        """
        data = {'username': 'admin', 'password': 'admin'}
        response = self.client.post('/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 200)
        token = response.json()

        token.update({'username': 'user1'})
        response = self.client.post('/authentication/register/', token, format='json')
        self.assertEqual(response.status_code, 400)

    def test_register_user_already_exist(self):
        """
        Test user registration when the user already exists.

        Logs in as an admin, attempts to register an existing user, and expects a 400 status code.

        :return: None
        """
        data = {'username': 'admin', 'password': 'admin'}
        response = self.client.post('/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 200)
        token = response.json()

        token.update(data)
        response = self.client.post('/authentication/register/', token, format='json')
        self.assertEqual(response.status_code, 400)

    def test_register(self):
        """
        Test user registration.

        Logs in as an admin, attempts to register a new user, and checks if the registration is successful.

        :return: None
        """
        data = {'username': 'admin', 'password': 'admin'}
        response = self.client.post('/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 200)
        token = response.json()

        token.update({'username': 'user1', 'password': 'pwd1'})
        response = self.client.post('/authentication/register/', token, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            sorted(list(response.json().keys())),
            ['token', 'user_pk']
        )
class TestRegisterPositive(StaticLiveServerTestCase):
    """
    Test class to verify positive user registration.

    This class inherits from LiveServerTestCase and performs user registration tests
    using an automated web browser.

    Methods:
    - setUp: Set up the test environment before each test.
    - tearDown: Perform cleanup tasks after each test.
    - test_register_positive: Perform a user registration test with valid data.
    """
    def setUp(self):
        """
        Set up the test environment before each test.

        Instantiate necessary objects for the test, such as the base configuration
        and a headless web browser.

        :return: None
        """
        self.base = BaseTestCase()
        self.base.setUp()

        options = webdriver.ChromeOptions()
        options.headless = True 
        self.cleaner = webdriver.Chrome(options=options)

        super().setUp()            
            
    def tearDown(self):
        """
        Perform cleanup tasks after each test.

        Close the web browser and perform additional cleanup tasks.

        :return: None
        """           
        super().tearDown()
        self.cleaner.quit()
        self.base.tearDown()
  
    def testregisterpositive(self):
        """
        Perform a user registration test with valid data.

        Open the registration page, fill out the form with valid data,
        and verify that the user is redirected correctly after registration.

        :return: None
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
    Test case class for negative scenarios in the registration process.

    Inherits from Django's LiveServerTestCase to test views with Selenium.
    """
    def setUp(self):
        """
        Set up the necessary resources for each test case.

        - Creates a base test case instance.
        - Sets up the base test case.
        - Initializes an API client.
        - Mocks a query using the client.
        - Creates a user for testing.
        - Configures a headless Chrome WebDriver.
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
        Clean up resources after each test case.

        - Closes the Chrome WebDriver.
        - Tears down the base test case.
        """           
        super().tearDown()
        self.cleaner.quit()
        self.base.tearDown()
  
    def testregisternegativewrongpassword(self):
        """
        Test negative registration scenario with a wrong password.

        - Navigates to the registration view.
        - Enters invalid data (different passwords).
        - Asserts that the page remains on the registration view.
        - Asserts that an alert indicates the password mismatch.
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
        Test negative registration scenario with a too long username.

        - Navigates to the registration view.
        - Enters invalid data (excessively long username).
        - Asserts that the page remains on the registration view.
        - Asserts that an alert indicates the username length violation.
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
        Test negative registration scenario with an already taken username.

        - Navigates to the registration view.
        - Enters invalid data (existing username).
        - Asserts that the page remains on the registration view.
        - Asserts that an alert indicates the username availability issue.
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
        Test negative registration scenario with a username not matching the pattern.

        - Navigates to the registration view.
        - Enters invalid data (username with invalid characters).
        - Asserts that the page remains on the registration view.
        - Asserts that an alert indicates the username pattern mismatch.
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
        """
        Test negative registration scenario with an already taken email.

        - Navigates to the registration view.
        - Enters invalid data (existing email).
        - Asserts that the page remains on the registration view.
        - Asserts that an alert indicates the email availability issue.
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
        Test negative registration scenario with an already taken email.

        - Navigates to the registration view.
        - Enters invalid data (existing email).
        - Asserts that the page remains on the registration view.
        - Asserts that an alert indicates the email availability issue.
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
        Test negative registration scenario with an already taken email.

        - Navigates to the registration view.
        - Enters invalid data (existing email).
        - Asserts that the page remains on the registration view.
        - Asserts that an alert indicates the email availability issue.
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
        Test negative registration scenario with a common password.

        - Navigates to the registration view.
        - Enters invalid data (common password).
        - Asserts that the page remains on the registration view.
        - Asserts that an alert indicates the use of a common password.
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
        Test negative registration scenario with a password similar to the username.

        - Navigates to the registration view.
        - Enters invalid data (password similar to the username).
        - Asserts that the page remains on the registration view.
        - Asserts that an alert indicates the password similarity issue.
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
        Test negative registration scenario with a numeric password.

        - Navigates to the registration view.
        - Enters invalid data (numeric password).
        - Asserts that the page remains on the registration view.
        - Asserts that an alert indicates the use of a numeric password.
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
    Test case for positive login scenarios.

    This class inherits from Django's StaticLiveServerTestCase and defines tests for successful user login.
    """
    def setUp(self):
        """
        Set up the test environment before each test.

        This method initializes necessary resources such as a base test case, a headless Chrome browser, and
        sets up the static live server.

        :return: None
        """
        self.base = BaseTestCase()
        self.base.setUp()

        options = webdriver.ChromeOptions()
        options.headless = True
        self.cleaner = webdriver.Chrome(options=options)

        super().setUp()            
            
    def tearDown(self):
        """
        Clean up the test environment after each test.

        This method quits the headless Chrome browser and performs teardown operations from the base test case.

        :return: None
        """           
        super().tearDown()
        self.cleaner.quit()
        self.base.tearDown()
  
    def testloginpositive(self):
        """
        Test the positive login scenario.

        This method navigates to the registration page, fills in the required information, submits the form,
        verifies the successful registration, and then logs in with the registered credentials, ensuring a
        successful login.

        :return: None
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
    Test case for negative login scenarios.

    This class inherits from Django's StaticLiveServerTestCase and defines tests for unsuccessful user login attempts.
    """
    def setUp(self):
        """
        Set up the test environment before each test.

        This method initializes necessary resources such as a base test case, a headless Chrome browser, and
        sets up the static live server.

        :return: None
        """
        self.base = BaseTestCase()
        self.base.setUp()

        options = webdriver.ChromeOptions()
        options.headless = True
        self.cleaner = webdriver.Chrome(options=options)

        super().setUp()            
            
    def tearDown(self):
        """
        Clean up the test environment after each test.

        This method quits the headless Chrome browser and performs teardown operations from the base test case.

        :return: None
        """           
        super().tearDown()
        self.cleaner.quit()
        self.base.tearDown()
  
    def testloginnegative(self):
        """
        Test negative login scenarios.

        This method navigates to the login page, provides invalid credentials, submits the form, and
        verifies that the login attempt fails.

        :return: None
        """
        self.cleaner.get(self.live_server_url+"/authentication/login-view/")
        
        self.cleaner.find_element(By.ID, "id_username").click()
        self.cleaner.find_element(By.ID, "id_username").send_keys("testnegative")
        self.cleaner.find_element(By.ID, "id_password1").click()
        self.cleaner.find_element(By.ID, "id_password1").send_keys("testnegative123")
        self.cleaner.find_element(By.CSS_SELECTOR, ".btn").click()

        
        self.assertTrue(self.cleaner.current_url == self.live_server_url+"/authentication/login-view/")
        self.assertTrue( self.cleaner.find_element(By.CSS_SELECTOR, ".alert").text == "This username or password do not exist")
        