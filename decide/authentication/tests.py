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