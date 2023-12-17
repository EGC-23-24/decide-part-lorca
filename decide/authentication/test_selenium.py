import time
from rest_framework.test import APIClient
from rest_framework.test import APITestCase

from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from base.tests import BaseTestCase 
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from base import mods
from selenium.webdriver.common.action_chains import ActionChains

from nose.tools import nottest


class TestRegisterPositive(StaticLiveServerTestCase):

    def setUp(self):
        self.base = BaseTestCase()
        self.base.setUp()

        options = webdriver.ChromeOptions()
        options.headless = True 
        self.driver = webdriver.Chrome(options=options)

        super().setUp()            
            
    def tearDown(self):           
        super().tearDown()
        self.driver.quit()
        self.base.tearDown()

    def testregisterpositive(self):
        self.driver.get(self.live_server_url+"/authentication/register-view/")
        self.driver.set_window_size(910, 1016)
        
        self.driver.find_element(By.ID, "id_username").click()
        self.driver.find_element(By.ID, "id_username").send_keys("testuser")
        self.driver.find_element(By.ID, "id_password1").click()
        self.driver.find_element(By.ID, "id_password1").send_keys("testpasword123")
        self.driver.find_element(By.ID, "id_password2").click()
        self.driver.find_element(By.ID, "id_password2").send_keys("testpasword123")
        self.driver.find_element(By.ID, "id_email").click()
        self.driver.find_element(By.ID, "id_email").send_keys("test@test.com")
        self.driver.find_element(By.ID, "id_first_name").click()
        self.driver.find_element(By.ID, "id_first_name").send_keys("Alex")
        element_last_name = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "id_last_name"))
        )
        element_last_name.click() 
        element_last_name.send_keys("Smith")
        self.driver.find_element(By.ID, "register_button").click()

        self.assertTrue(self.driver.current_url == self.live_server_url+"/")

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
        self.driver = webdriver.Chrome(options=options)

        super().setUp()            
            
    def tearDown(self):           
        super().tearDown()
        self.driver.quit()
        self.base.tearDown()
  
    def testregisternegativewrongpassword(self):
        self.driver.get(self.live_server_url+"/authentication/register-view/")
        self.driver.set_window_size(910, 1016)
        
        self.driver.find_element(By.ID, "id_username").click()
        self.driver.find_element(By.ID, "id_username").send_keys("testuser")
        self.driver.find_element(By.ID, "id_password1").click()
        self.driver.find_element(By.ID, "id_password1").send_keys("testpasword123")
        self.driver.find_element(By.ID, "id_password2").click()
        self.driver.find_element(By.ID, "id_password2").send_keys("testpasword12")
        self.driver.find_element(By.ID, "id_email").click()
        self.driver.find_element(By.ID, "id_email").send_keys("test@test.com")
        self.driver.find_element(By.ID, "id_first_name").click()
        self.driver.find_element(By.ID, "id_first_name").send_keys("Alex")
        element_last_name = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "id_last_name"))
        )
        element_last_name.click() 
        element_last_name.send_keys("Smith")
        self.driver.find_element(By.ID, "register_button").click()

        self.assertTrue(self.driver.current_url == self.live_server_url+"/authentication/register-view/")
        self.assertTrue(self.driver.find_element(By.CSS_SELECTOR, ".alert").text == "Passwords must be the same")

    def testregisternegativelongusername(self):
        self.driver.get(self.live_server_url+"/authentication/register-view/")
        self.driver.set_window_size(910, 1016)
        
        self.driver.find_element(By.ID, "id_username").click()
        self.driver.find_element(By.ID, "id_username").send_keys("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
        self.driver.find_element(By.ID, "id_password1").click()
        self.driver.find_element(By.ID, "id_password1").send_keys("testpasword123")
        self.driver.find_element(By.ID, "id_password2").click()
        self.driver.find_element(By.ID, "id_password2").send_keys("testpasword123")
        self.driver.find_element(By.ID, "id_email").click()
        self.driver.find_element(By.ID, "id_email").send_keys("test1@test.com")
        self.driver.find_element(By.ID, "id_first_name").click()
        self.driver.find_element(By.ID, "id_first_name").send_keys("Alex")
        element_last_name = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "id_last_name"))
        )
        element_last_name.click() 
        element_last_name.send_keys("Smith")
        self.driver.find_element(By.ID, "register_button").click()

        self.assertTrue(self.driver.current_url == self.live_server_url+"/authentication/register-view/")
        self.assertTrue(self.driver.find_element(By.CSS_SELECTOR, ".alert").text == "This username is larger than 150 characters")

    def testregisternegativeusername(self):
        self.driver.get(self.live_server_url+"/authentication/register-view/")
        self.driver.set_window_size(910, 1016)
        
        self.driver.find_element(By.ID, "id_username").click()
        self.driver.find_element(By.ID, "id_username").send_keys("prueba1")
        self.driver.find_element(By.ID, "id_password1").click()
        self.driver.find_element(By.ID, "id_password1").send_keys("testpasword123")
        self.driver.find_element(By.ID, "id_password2").click()
        self.driver.find_element(By.ID, "id_password2").send_keys("testpasword123")
        self.driver.find_element(By.ID, "id_email").click()
        self.driver.find_element(By.ID, "id_email").send_keys("test2@test.com")
        self.driver.find_element(By.ID, "id_first_name").click()
        self.driver.find_element(By.ID, "id_first_name").send_keys("Alex")
        element_last_name = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "id_last_name"))
        )
        element_last_name.click() 
        element_last_name.send_keys("Smith")
        self.driver.find_element(By.ID, "register_button").click()

        self.assertTrue(self.driver.current_url == self.live_server_url+"/authentication/register-view/")
        self.assertTrue(self.driver.find_element(By.CSS_SELECTOR, ".alert").text == "This username has already taken")

    def testregisternegativepatternusername(self):
        self.driver.get(self.live_server_url+"/authentication/register-view/")
        self.driver.set_window_size(910, 1016)
        
        self.driver.find_element(By.ID, "id_username").click()
        self.driver.find_element(By.ID, "id_username").send_keys("test$%&user")
        self.driver.find_element(By.ID, "id_password1").click()
        self.driver.find_element(By.ID, "id_password1").send_keys("testpasword123")
        self.driver.find_element(By.ID, "id_password2").click()
        self.driver.find_element(By.ID, "id_password2").send_keys("testpasword123")
        self.driver.find_element(By.ID, "id_email").click()
        self.driver.find_element(By.ID, "id_email").send_keys("test4@test.com")
        self.driver.find_element(By.ID, "id_first_name").click()
        self.driver.find_element(By.ID, "id_first_name").send_keys("Alex")
        element_last_name = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "id_last_name"))
        )
        element_last_name.click() 
        element_last_name.send_keys("Smith")
        self.driver.find_element(By.ID, "register_button").click()

        self.assertTrue(self.driver.current_url == self.live_server_url+"/authentication/register-view/")
        self.assertTrue(self.driver.find_element(By.CSS_SELECTOR, ".alert").text == "This username not match with the pattern")

    @nottest
    def testregisternegativeemail(self):
        self.driver.get(self.live_server_url+"/authentication/register-view/")
        self.driver.set_window_size(910, 1016)
    
        self.driver.find_element(By.ID, "id_username").click()
        self.driver.find_element(By.ID, "id_username").send_keys("testuser5")
        self.driver.find_element(By.ID, "id_password1").click()
        self.driver.find_element(By.ID, "id_password1").send_keys("testpasword123")
        self.driver.find_element(By.ID, "id_password2").click()
        self.driver.find_element(By.ID, "id_password2").send_keys("testpasword123")
        self.driver.find_element(By.ID, "id_email").click()
        self.driver.find_element(By.ID, "id_email").send_keys("test@gmail.com")
        self.driver.find_element(By.ID, "id_first_name").click()
        self.driver.find_element(By.ID, "id_first_name").send_keys("Alex")
        element_last_name = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "id_last_name"))
        )
        element_last_name.click() 
        element_last_name.send_keys("Smith")
        self.driver.find_element(By.ID, "register_button").click()

        self.assertTrue(self.driver.current_url == self.live_server_url+"/authentication/register-view/")
        self.assertTrue(self.driver.find_element(By.CSS_SELECTOR, ".alert").text == "This email has already taken")

    def testregisternegativecommonpass(self):
        self.driver.get(self.live_server_url+"/authentication/register-view/")
        self.driver.set_window_size(910, 1016)
        
        self.driver.find_element(By.ID, "id_username").click()
        self.driver.find_element(By.ID, "id_username").send_keys("testuser7")
        self.driver.find_element(By.ID, "id_password1").click()
        self.driver.find_element(By.ID, "id_password1").send_keys("12345678")
        self.driver.find_element(By.ID, "id_password2").click()
        self.driver.find_element(By.ID, "id_password2").send_keys("12345678")
        self.driver.find_element(By.ID, "id_email").click()
        self.driver.find_element(By.ID, "id_email").send_keys("test7@test.com")
        self.driver.find_element(By.ID, "id_first_name").click()
        self.driver.find_element(By.ID, "id_first_name").send_keys("Alex")
        element_last_name = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "id_last_name"))
        )
        element_last_name.click() 
        element_last_name.send_keys("Smith")
        self.driver.find_element(By.ID, "register_button").click()

        self.assertTrue(self.driver.current_url == self.live_server_url+"/authentication/register-view/")
        self.assertTrue(self.driver.find_element(By.CSS_SELECTOR, ".alert").text == "This password is a common password")

    def testregisternegativesimilarpass(self):
        self.driver.get(self.live_server_url+"/authentication/register-view/")
        self.driver.set_window_size(910, 1016)
        
        self.driver.find_element(By.ID, "id_username").click()
        self.driver.find_element(By.ID, "id_username").send_keys("testuser8")
        self.driver.find_element(By.ID, "id_password1").click()
        self.driver.find_element(By.ID, "id_password1").send_keys("testuser8")
        self.driver.find_element(By.ID, "id_password2").click()
        self.driver.find_element(By.ID, "id_password2").send_keys("testuser8")
        self.driver.find_element(By.ID, "id_email").click()
        self.driver.find_element(By.ID, "id_email").send_keys("test8@test.com")
        self.driver.find_element(By.ID, "id_first_name").click()
        self.driver.find_element(By.ID, "id_first_name").send_keys("Alex")
        element_last_name = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "id_last_name"))
        )
        element_last_name.click() 
        element_last_name.send_keys("Smith")
        self.driver.find_element(By.ID, "register_button").click()

        self.assertTrue(self.driver.current_url == self.live_server_url+"/authentication/register-view/")
        self.assertTrue(self.driver.find_element(By.CSS_SELECTOR, ".alert").text == "This password is too similar to your personal data")

    def testregisternegativenumericpass(self):
        self.driver.get(self.live_server_url+"/authentication/register-view/")
        self.driver.set_window_size(910, 1016)
        
        self.driver.find_element(By.ID, "id_username").click()
        self.driver.find_element(By.ID, "id_username").send_keys("testuser9")
        self.driver.find_element(By.ID, "id_password1").click()
        self.driver.find_element(By.ID, "id_password1").send_keys("638372334453")
        self.driver.find_element(By.ID, "id_password2").click()
        self.driver.find_element(By.ID, "id_password2").send_keys("638372334453")
        self.driver.find_element(By.ID, "id_email").click()
        self.driver.find_element(By.ID, "id_email").send_keys("test9@test.com")
        self.driver.find_element(By.ID, "id_first_name").click()
        self.driver.find_element(By.ID, "id_first_name").send_keys("Alex")
        element_last_name = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "id_last_name"))
        )
        element_last_name.click() 
        element_last_name.send_keys("Smith")
        self.driver.find_element(By.ID, "register_button").click()

        self.assertTrue(self.driver.current_url == self.live_server_url+"/authentication/register-view/")
        self.assertTrue(self.driver.find_element(By.CSS_SELECTOR, ".alert").text == "This password is numeric")



class TestLoginPositive(StaticLiveServerTestCase):

    def setUp(self):
        self.base = BaseTestCase()
        self.base.setUp()

        options = webdriver.ChromeOptions()
        options.headless = True
        self.driver = webdriver.Chrome(options=options)


        super().setUp()            
            
    def tearDown(self):           
        super().tearDown()
        self.driver.quit()
        self.base.tearDown()
  
    def testloginpositive(self):
        self.driver.get(self.live_server_url+"/authentication/register-view/")
        self.driver.set_window_size(910, 1016)
        
        self.driver.find_element(By.ID, "id_username").click()
        self.driver.find_element(By.ID, "id_username").send_keys("testlogin")
        self.driver.find_element(By.ID, "id_password1").click()
        self.driver.find_element(By.ID, "id_password1").send_keys("login1234")
        self.driver.find_element(By.ID, "id_password2").click()
        self.driver.find_element(By.ID, "id_password2").send_keys("login1234")
        self.driver.find_element(By.ID, "id_email").click()
        self.driver.find_element(By.ID, "id_email").send_keys("login@test.com")
        self.driver.find_element(By.ID, "id_first_name").click()
        self.driver.find_element(By.ID, "id_first_name").send_keys("Alex")
        element_last_name = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "id_last_name"))
        )
        element_last_name.click() 
        element_last_name.send_keys("Smith")
        self.driver.find_element(By.ID, "register_button").click()

        self.assertTrue(self.driver.current_url == self.live_server_url+"/")

        self.driver.get(self.live_server_url+"/authentication/login-view/")

        self.driver.find_element(By.ID, "id_username").click()
        self.driver.find_element(By.ID, "id_username").send_keys("testlogin")
        self.driver.find_element(By.ID, "id_password1").click()
        self.driver.find_element(By.ID, "id_password1").send_keys("login1234")
        self.driver.find_element(By.ID, "login_button").click()

        self.assertTrue(self.driver.current_url == self.live_server_url+"/")

class TestLoginNegative(StaticLiveServerTestCase):

    def setUp(self):
        self.base = BaseTestCase()
        self.base.setUp()

        options = webdriver.ChromeOptions()
        options.headless = True
        self.driver = webdriver.Chrome(options=options)

        super().setUp()            
            
    def tearDown(self):           
        super().tearDown()
        self.driver.quit()
        self.base.tearDown()
  
    def testloginnegative(self):
        self.driver.get(self.live_server_url+"/authentication/login-view/")
        
        self.driver.find_element(By.ID, "id_username").click()
        self.driver.find_element(By.ID, "id_username").send_keys("testnegative")
        self.driver.find_element(By.ID, "id_password1").click()
        self.driver.find_element(By.ID, "id_password1").send_keys("testnegative123")
        self.driver.find_element(By.ID, "login_button").click()

        
        self.assertTrue(self.driver.current_url == self.live_server_url+"/authentication/login-view/")
        self.assertTrue(self.driver.find_element(By.CSS_SELECTOR, ".alert").text == "This username or password do not exist")

        