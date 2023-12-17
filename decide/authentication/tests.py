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

    def setUp(self):
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
        self.client = None

    def test_login(self):
        data = {'username': 'voter1', 'password': '123'}
        response = self.client.post('/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 200)

        token = response.json()
        self.assertTrue(token.get('token'))

    def test_login_fail(self):
        data = {'username': 'voter1', 'password': '321'}
        response = self.client.post('/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_getuser(self):
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
        token = {'token': 'invented'}
        response = self.client.post('/authentication/getuser/', token, format='json')
        self.assertEqual(response.status_code, 404)

    def test_getuser_invalid_token(self):
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
        data = {'username': 'voter1', 'password': '123'}
        response = self.client.post('/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 200)
        token = response.json()

        token.update({'username': 'user1'})
        response = self.client.post('/authentication/register/', token, format='json')
        self.assertEqual(response.status_code, 401)

    def test_register_bad_request(self):
        data = {'username': 'admin', 'password': 'admin'}
        response = self.client.post('/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 200)
        token = response.json()

        token.update({'username': 'user1'})
        response = self.client.post('/authentication/register/', token, format='json')
        self.assertEqual(response.status_code, 400)

    def test_register_user_already_exist(self):
        data = {'username': 'admin', 'password': 'admin'}
        response = self.client.post('/authentication/login/', data, format='json')
        self.assertEqual(response.status_code, 200)
        token = response.json()

        token.update(data)
        response = self.client.post('/authentication/register/', token, format='json')
        self.assertEqual(response.status_code, 400)

    def test_register(self):
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

    def setUp(self):
        self.base = BaseTestCase()
        self.base.setUp()

        options = webdriver.ChromeOptions()
        options.headless = True 
        self.cleaner = webdriver.Chrome(options=options)

        super().setUp()            
            
    def tearDown(self):           
        super().tearDown()
        self.cleaner.quit()
        self.base.tearDown()
  
    def testregisterpositive(self):
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

    def setUp(self):
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
        super().tearDown()
        self.cleaner.quit()
        self.base.tearDown()
  
    def testregisternegativewrongpassword(self):
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

    def setUp(self):
        self.base = BaseTestCase()
        self.base.setUp()

        options = webdriver.ChromeOptions()
        options.headless = True
        self.cleaner = webdriver.Chrome(options=options)

        super().setUp()            
            
    def tearDown(self):           
        super().tearDown()
        self.cleaner.quit()
        self.base.tearDown()
  
    def testloginpositive(self):
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

    def setUp(self):
        self.base = BaseTestCase()
        self.base.setUp()

        options = webdriver.ChromeOptions()
        options.headless = True
        self.cleaner = webdriver.Chrome(options=options)

        super().setUp()            
            
    def tearDown(self):           
        super().tearDown()
        self.cleaner.quit()
        self.base.tearDown()
  
    def testloginnegative(self):
        self.cleaner.get(self.live_server_url+"/authentication/login-view/")
        
        self.cleaner.find_element(By.ID, "id_username").click()
        self.cleaner.find_element(By.ID, "id_username").send_keys("testnegative")
        self.cleaner.find_element(By.ID, "id_password1").click()
        self.cleaner.find_element(By.ID, "id_password1").send_keys("testnegative123")
        self.cleaner.find_element(By.CSS_SELECTOR, ".btn").click()

        
        self.assertTrue(self.cleaner.current_url == self.live_server_url+"/authentication/login-view/")
        self.assertTrue( self.cleaner.find_element(By.CSS_SELECTOR, ".alert").text == "This username or password do not exist")
        