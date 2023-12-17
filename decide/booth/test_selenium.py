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
    # Clase de prueba para verificar la funcionalidad del sistema de selección múltiple en una cabina de votación.

    def create_voting(self):
        # Método para crear una instancia de votación de prueba con una pregunta y opciones.
        # Crea una pregunta con cinco opciones y la guarda en la base de datos junto con una instancia de votación.
        
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
        # Método para obtener o crear un usuario en la base de datos con un ID específico.

        user, _ = User.objects.get_or_create(pk=pk)
        user.username = 'user{}'.format(pk)
        user.set_password('qwerty')
        user.save()
        return user
      
    def setUp(self):
        # Preparación de la configuración inicial para las pruebas.
        # Crea un entorno básico para las pruebas con un usuario administrador y uno no administrador.
        # Configura una instancia de votación con una pregunta, opciones y comienza la votación.
        # Inicializa un navegador Chrome en modo headless para simular interacciones.

        #Crea un usuario admin y otro no admin
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
        # Método para limpiar y cerrar los recursos después de cada prueba.
        # Cierra el navegador y realiza la limpieza necesaria en la base de datos.   
            
        super().tearDown()
        self.driver.quit()

        self.base.tearDown()
    
    def test_question_multiple_options(self):
        # Prueba el proceso de selección múltiple donde se seleccionan tres opciones.
        # Verifica si las opciones se muestran correctamente en la interfaz.

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
        WebDriverWait(self.driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "form:nth-child(2) > .form-check"))
            )
        self.driver.find_element(By.CSS_SELECTOR, "form:nth-child(2) > .form-check").click()
        WebDriverWait(self.driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "form:nth-child(2) > .form-check"))
            )
        self.driver.find_element(By.CSS_SELECTOR, "form:nth-child(3) > .form-check").click()
        
        checkboxes = self.driver.find_elements(By.CSS_SELECTOR, '.form-check input[type="checkbox"]')

        selected_checkboxes = [checkbox for checkbox in checkboxes if checkbox.is_selected()]
        self.assertTrue(len(selected_checkboxes)==3)
        self.assertTrue(len(self.driver.find_elements(By.CSS_SELECTOR, 'form'))==5)
    
# @nottest
class CommentBoothTest(StaticLiveServerTestCase):
    # Clase de prueba para verificar la funcionalidad del sistema de comentarios en una cabina de votación.
    
    def create_voting(self):
        # Método para crear una instancia de votación de prueba con una pregunta y opciones.
        # Crea una pregunta y la guarda en la base de datos junto con una instancia de votación.

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
        # Método para obtener o crear un usuario en la base de datos con un ID específico.

        user, _ = User.objects.get_or_create(pk=pk)
        user.username = 'user{}'.format(pk)
        user.set_password('qwerty')
        user.save()
        return user

    def setUp(self):
        # Preparación de la configuración inicial para las pruebas.
        # Crea un entorno básico para las pruebas con un usuario administrador y uno no administrador.
        # Configura una instancia de votación con una pregunta, opciones y comienza la votación.
        # Inicializa un navegador Chrome en modo headless para simular interacciones.

        #Crea un usuario admin y otro no admin
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
        # Método para limpiar y cerrar los recursos después de cada prueba.
        # Cierra el navegador y realiza la limpieza necesaria en la base de datos.   
                
        super().tearDown()
        self.driver.quit()

        self.base.tearDown()

    def test_comment_question(self):
        # Prueba el proceso de comentarios donde se escribe un comentario.
        # Verifica si el comentario se muestra correctamente en la interfaz.

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
        text_area = self.driver.find_element(By.ID, "floatingTextarea2")
        text_area.click()
        text_area.send_keys("Comentario de prueba")
        self.driver.find_element(By.ID, "send-vote").click()
        
        # Verificar que la votación se realizó correctamente
        self.assertTrue(self.driver.find_element(By.XPATH, "//h1[contains(.,'Voting ID:')]").is_displayed())
        self.assertTrue(self.driver.find_element(By.ID, "floatingTextarea2").is_displayed())
        self.assertEquals(text_area.get_attribute('value'),"Comentario de prueba")

# @nottest
class YesNoBoothTest(StaticLiveServerTestCase):
    # Clase de prueba para verificar la funcionalidad del sistema de si/no en una cabina de votación.

    def create_voting(self):
        # Método para crear una instancia de votación de prueba con una pregunta y opciones.
        # Crea una pregunta y la guarda en la base de datos junto con una instancia de votación.

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
        # Método para obtener o crear un usuario en la base de datos con un ID específico.

        user, _ = User.objects.get_or_create(pk=pk)
        user.username = 'user{}'.format(pk)
        user.set_password('qwerty')
        user.save()
        return user
    
    def setUp(self):
        # Preparación de la configuración inicial para las pruebas.
        # Crea un entorno básico para las pruebas con un usuario administrador y uno no administrador.
        # Configura una instancia de votación con una pregunta, opciones y comienza la votación.
        # Inicializa un navegador Chrome en modo headless para simular interacciones.

        #Crea un usuario admin y otro no admin
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
        # Método para limpiar y cerrar los recursos después de cada prueba.
        # Cierra el navegador y realiza la limpieza necesaria en la base de datos.   

        super().tearDown()
        self.driver.quit()

        self.base.tearDown()  
    
    def test_question_yesno(self):
        # Prueba el proceso de si/no donde se selecciona la opción "Sí".
        # Verifica si la opción se muestra correctamente en la interfaz.

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
        
        login = WebDriverWait(self.driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn-success"))
            )
        login.click()

        self.assertTrue(self.driver.find_element(By.XPATH, "//h1[contains(.,'Voting ID:')]").is_displayed())
        self.assertTrue(self.driver.find_element(By.ID, "yesbutton").is_displayed())
        self.assertTrue(self.driver.find_element(By.ID, "nobutton").is_displayed())

# @nottest
class PreferenceBoothTest(StaticLiveServerTestCase):
    # Clase de prueba para verificar la funcionalidad del sistema de preferencias en una cabina de votación.

    def create_voting(self):
        # Método para crear una instancia de votación de prueba con una pregunta y opciones.
        # Crea una pregunta con tres opciones y la guarda en la base de datos junto con una instancia de votación.

        q = Question(desc='test question', type='R')
        q.save()
        opt1 = QuestionOptionRanked(question=q, option='Test 1', number=1)
        opt2 = QuestionOptionRanked(question=q, option='Test 2', number=2)
        opt3 = QuestionOptionRanked(question=q, option='Test 3', number=3)
        opt1.save()
        opt2.save()
        opt3.save()
        v = Voting(name='test voting', question=q)
        v.save()

        a, _ = Auth.objects.get_or_create(url=settings.BASEURL,
                                          defaults={'me': True, 'name': 'test auth'})
        a.save()
        v.auths.add(a)
        return v

    def get_or_create_user(self,pk):
        # Método para obtener o crear un usuario en la base de datos con un ID específico.
        user, _ = User.objects.get_or_create(pk=pk)
        user.username = f'user{pk}'
        user.set_password('qwerty')
        user.save()
        return user

    def setUp(self):
        # Preparación de la configuración inicial para las pruebas.
        # Crea un entorno básico para las pruebas con un usuario administrador y uno no administrador.
        # Configura una instancia de votación con una pregunta, opciones y comienza la votación.
        # Inicializa un navegador Chrome en modo headless para simular interacciones.
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
        # Método para limpiar y cerrar los recursos después de cada prueba.
        # Cierra el navegador y realiza la limpieza necesaria en la base de datos.   
        super().tearDown()
        self.driver.quit()

        self.base.tearDown()

    def login_user(self, username, password):
        # Método para realizar el inicio de sesión de un usuario en el sistema de votación simulando la interacción con la interfaz.
        self.driver.find_element(By.ID, "menu-toggle").click()
        
        goto_logging = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.ID, "goto-logging-button"))
        )
        goto_logging.click()

        username_field = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.ID, "username"))
        )
        username_field.click()
        
        self.driver.find_element(By.ID, "username").send_keys(username)
        self.driver.find_element(By.ID, "password").click()
        self.driver.find_element(By.ID, "password").send_keys(password, Keys.ENTER)
        login = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.ID, "process-login-button"))
        )
        login.click()

    def select_preferences(self, preferences):
        # Método para seleccionar preferencias en la interfaz de usuario durante la votación.
        inputs = WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.ID, "rankingInput"))
        )

        for index, input_element in enumerate(inputs):
            input_element.click()
            input_element.send_keys(str(preferences[index]))

    def perform_preference(self, preferences, expected_values):
        # Método que simula el proceso completo de preferencias durante una votación.
        # Inicia sesión, elige las preferencias y verifica si se muestran correctamente en la interfaz.
        self.driver.get(f'{self.live_server_url}/booth/{self.v.id}/')
        self.driver.set_window_size(910, 1016)
        self.login_user("user1", "qwerty")
        self.select_preferences(preferences)
        self.driver.find_element(By.CSS_SELECTOR, ".btn-primary").click()

        self.assertTrue(self.driver.find_element(By.XPATH, f"//h1[contains(.,'Voting ID:')]").is_displayed())

        inputs = WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.ID, "rankingInput"))
        )

        for index, input_element in enumerate(inputs):
            expected_value = str(expected_values.get(index, ""))
            actual_value = input_element.get_attribute('value')
            self.assertEquals(actual_value, expected_value)

    def test_question_preference(self):
        # Prueba el proceso de preferencias donde se asignan valores consecutivos a las opciones.
        # Verifica si las preferencias se muestran correctamente en la interfaz.
        preferences = [1, 2, 3]
        expected_values = {0: '1', 1: '2', 2: '3'}
        self.perform_preference(preferences, expected_values)

    def test_preference_booth_same_preference(self):
        # Prueba el proceso de preferencias donde se asignan valores repetidos a las opciones.
        # Verifica si las preferencias se muestran correctamente en la interfaz.

        preferences = [1, 1, 2]
        expected_values = {0: '1', 1: '1', 2: '2'}
        self.perform_preference(preferences, expected_values)

    def test_preference_booth_no_fullfill_all_preferences(self):
        # Prueba el proceso de preferencias donde no se completan todas las preferencias.
        # Verifica si las preferencias se muestran correctamente en la interfaz.
        preferences = [1,"",""]
        expected_values = {0: '1', 1: '', 2: ''}
        self.perform_preference(preferences, expected_values)