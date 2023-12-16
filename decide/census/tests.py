import random
from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.conf import settings
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from openpyxl import load_workbook
from io import BytesIO
from openpyxl import Workbook
from django.core.files.uploadedfile import SimpleUploadedFile

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

from .models import Census
from voting.models import Voting, Question, QuestionOption
from base.models import Auth
from base import mods
from base.tests import BaseTestCase
from datetime import datetime


class CensusTestCase(BaseTestCase):

    def setUp(self):
        # Crear una votación
        q = Question(desc="test question")
        q.save()
        for i in range(5):
            opt = QuestionOption(question=q, option="option {}".format(i + 1))
            opt.save()
        v = Voting(name="test voting", question=q)
        v.save()

        # Crear un votante
        u, created = User.objects.get_or_create(username='testvoter')
        u.is_active = True
        u.save()

        # Crear un censo
        self.census = Census.objects.create(voting_id=v.id, voter_id=u.id)

        super().setUp()
    
    def test_create_census(self):
        # Crear una votación
        q = Question(desc="test question")
        q.save()
        for i in range(5):
            opt = QuestionOption(question=q, option="option {}".format(i + 1))
            opt.save()
        v = Voting(name="test voting", question=q)
        v.save()

        # Crear un votante
        u, created = User.objects.get_or_create(username='testvoter')
        u.is_active = True
        u.save()

        # Crear un censo
        census = Census.objects.create(voting_id=v.id, voter_id=u.id)

        # Comprobar que se ha creado correctamente
        self.assertEqual(census.voting_id, v.id)
        self.assertEqual(census.voter_id, u.id)
        self.assertEqual(Census.objects.latest('id').voting_id, v.id)
        self.assertEqual(Census.objects.latest('id').voter_id, u.id)

    def test_create_census_invalid_voting_id(self):
        # Crear una votación
        q = Question(desc="test question")
        q.save()
        for i in range(5):
            opt = QuestionOption(question=q, option="option {}".format(i + 1))
            opt.save()
        v = Voting(name="test voting", question=q)
        v.save()

        # Crear un votante
        u, created = User.objects.get_or_create(username='testvoter')
        u.is_active = True
        u.save()

        with self.assertRaises(ValueError):
            # Crear un censo
            census = Census.objects.create(voting_id="invalid_voting_id", voter_id=u.id)
            census.full_clean()  # This should raise a ValidationError exception

    def test_create_census_invalid_voter_id(self):
        # Crear una votación
        q = Question(desc="test question")
        q.save()
        for i in range(5):
            opt = QuestionOption(question=q, option="option {}".format(i + 1))
            opt.save()
        v = Voting(name="test voting", question=q)
        v.save()

        # Crear un votante
        u, created = User.objects.get_or_create(username='testvoter')
        u.is_active = True
        u.save()

        with self.assertRaises(ValueError):
            # Attempt to create a census with an invalid voter_id
            census = Census.objects.create(voting_id=v.id, voter_id="invalid_voter_id")
            census.full_clean()

    def test_create_census_invalid_voting_id_and_voter_id(self):
        with self.assertRaises(ValueError):
            # Attempt to create a census with an invalid voting_id and voter_id
            census = Census.objects.create(voting_id="invalid_voting_id", voter_id="invalid_voter_id")
            census.full_clean()

    def test_delete_census(self):
        # Delete any existing Census objects to avoid IntegrityError
        Census.objects.all().delete()

        # Crear una votación
        q = Question(desc="test question")
        q.save()
        for i in range(5):
            opt = QuestionOption(question=q, option="option {}".format(i + 1))
            opt.save()
        v = Voting(name="test voting", question=q)
        v.save()

        # Crear un votante
        u, created = User.objects.get_or_create(username='testvoter')
        u.is_active = True
        u.save()
        
        # Create a Census object to delete
        census_to_delete = Census.objects.create(voting_id=v.id, voter_id=u.id)

        # Define the URL and the data
        url = reverse('census_deleted')  # replace with your URL name
        data = {'voting_id': census_to_delete.voting_id, 'voter_id': census_to_delete.voter_id}

        # Make the POST request
        response = self.client.post(url, data, follow=True)

        # Check the status code and the response data
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Census.objects.filter(voting_id=census_to_delete.voting_id, voter_id=census_to_delete.voter_id).exists())
            
    def test_delete_census_invalid_voting_id(self):
        # Crear una votación
        q = Question(desc="test question")
        q.save()
        for i in range(5):
            opt = QuestionOption(question=q, option="option {}".format(i + 1))
            opt.save()
        v = Voting(name="test voting", question=q)
        v.save()

        # Crear un votante
        u, created = User.objects.get_or_create(username='testvoter')
        u.is_active = True
        u.save()

        with self.assertRaises(ValueError):
            # Attempt to delete a census with an invalid voting_id
            census = Census.objects.create(voting_id="invalid_voting_id", voter_id=u.id)
            census.full_clean()
    
    def test_delete_census_invalid_voter_id(self):
        # Crear una votación
        q = Question(desc="test question")
        q.save()
        for i in range(5):
            opt = QuestionOption(question=q, option="option {}".format(i + 1))
            opt.save()
        v = Voting(name="test voting", question=q)
        v.save()

        # Crear un votante
        u, created = User.objects.get_or_create(username='testvoter')
        u.is_active = True
        u.save()

        with self.assertRaises(ValueError):
            # Attempt to delete a census with an invalid voter_id
            census = Census.objects.create(voting_id=v.id, voter_id="invalid_voter_id")
            census.full_clean()
    
    def test_delete_census_invalid_voting_id_and_voter_id(self):
        with self.assertRaises(ValueError):
            # Attempt to delete a census with an invalid voting_id and voter_id
            census = Census.objects.create(voting_id="invalid_voting_id", voter_id="invalid_voter_id")
            census.full_clean()

    def test_list_census(self):
        # Eliminar todos los objetos Census existentes
        Census.objects.all().delete()

        # Crear un votante
        u, created = User.objects.get_or_create(username='testvoter')
        u.is_active = True
        u.save()

        # Crear una votación
        q = Question(desc="test question")
        q.save()
        for i in range(5):
            opt = QuestionOption(question=q, option="option {}".format(i + 1))
            opt.save()
        v = Voting(name="test voting", question=q)
        v.save()

        # Agregar el votante al censo
        census = Census(voter_id=u.id, voting_id=v.id)
        census.save()

        # Define the URL and the data
        url = reverse('census_list')

        # Make the POST request
        response = self.client.get(url, follow=True)

        # Check the status code and the response data
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Census.objects.count(), 1)
        # Comprobar que el voting_id del objeto Census es el correcto
        self.assertEqual(Census.objects.latest('id').voting_id, v.id)
        self.assertEqual(Census.objects.latest('id').voter_id, u.id)

    def test_list_census_invalid_voting_id(self):
        # Crear una votación
        q = Question(desc="test question")
        q.save()
        for i in range(5):
            opt = QuestionOption(question=q, option="option {}".format(i + 1))
            opt.save()
        v = Voting(name="test voting", question=q)
        v.save()

        # Crear un votante
        u, created = User.objects.get_or_create(username='testvoter')
        u.is_active = True
        u.save()

        with self.assertRaises(ValueError):
            # Attempt to list a census with an invalid voting_id
            census = Census.objects.create(voting_id="invalid_voting_id", voter_id=u.id)
            census.full_clean()
    
    def test_list_census_invalid_voter_id(self):
        # Crear una votación
        q = Question(desc="test question")
        q.save()
        for i in range(5):
            opt = QuestionOption(question=q, option="option {}".format(i + 1))
            opt.save()
        v = Voting(name="test voting", question=q)
        v.save()

        # Crear un votante
        u, created = User.objects.get_or_create(username='testvoter')
        u.is_active = True
        u.save()

        with self.assertRaises(ValueError):
            # Attempt to list a census with an invalid voter_id
            census = Census.objects.create(voting_id=v.id, voter_id="invalid_voter_id")
            census.full_clean()

    def test_list_census_invalid_voting_id_and_voter_id(self):
        with self.assertRaises(ValueError):
            # Attempt to list a census with an invalid voting_id and voter_id
            census = Census.objects.create(voting_id="invalid_voting_id", voter_id="invalid_voter_id")
            census.full_clean()

    def test_get_census(self):
        # Eliminar todos los objetos Census existentes
        Census.objects.all().delete()

        # Crear un votante
        u, created = User.objects.get_or_create(username='testvoter')
        u.is_active = True
        u.save()

        # Crear una votación
        q = Question(desc="test question")
        q.save()
        for i in range(5):
            opt = QuestionOption(question=q, option="option {}".format(i + 1))
            opt.save()
        v = Voting(name="test voting", question=q)
        v.save()

        # Agregar el votante al censo
        census = Census(voter_id=u.id, voting_id=v.id)
        census.save()

        # Define the URL and the data
        url = reverse('census_details')

        data = {'id': census.id}
        # Make the POST request
        response = self.client.get(url, data)

        # Check the status code and the response data
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Census.objects.count(), 1)
        self.assertEqual(Census.objects.latest('id').voting_id, v.id)
        self.assertEqual(Census.objects.latest('id').voter_id, u.id)

    def test_get_census_invalid_voting_id(self):
        # Crear una votación
        q = Question(desc="test question")
        q.save()
        for i in range(5):
            opt = QuestionOption(question=q, option="option {}".format(i + 1))
            opt.save()
        v = Voting(name="test voting", question=q)
        v.save()

        # Crear un votante
        u, created = User.objects.get_or_create(username='testvoter')
        u.is_active = True
        u.save()

        with self.assertRaises(ValueError):
            # Attempt to get a census with an invalid voting_id
            census = Census.objects.create(voting_id="invalid_voting_id", voter_id=u.id)
            census.full_clean()
    
    def test_get_census_invalid_voter_id(self):
        # Crear una votación
        q = Question(desc="test question")
        q.save()
        for i in range(5):
            opt = QuestionOption(question=q, option="option {}".format(i + 1))
            opt.save()
        v = Voting(name="test voting", question=q)
        v.save()

        # Crear un votante
        u, created = User.objects.get_or_create(username='testvoter')
        u.is_active = True
        u.save()

        with self.assertRaises(ValueError):
            # Attempt to get a census with an invalid voter_id
            census = Census.objects.create(voting_id=v.id, voter_id="invalid_voter_id")
            census.full_clean()

    def test_get_census_invalid_voting_id_and_voter_id(self):
        with self.assertRaises(ValueError):
            # Attempt to get a census with an invalid voting_id and voter_id
            census = Census.objects.create(voting_id="invalid_voting_id", voter_id="invalid_voter_id")
            census.full_clean()

            

    def tearDown(self):
        super().tearDown()
        self.census = None

    def test_check_vote_permissions(self):
        # Crear un votante
        u, created = User.objects.get_or_create(username='testvoter')
        u.is_active = True
        u.save()

        # Crear una votación
        q = Question(desc="test question")
        q.save()
        for i in range(5):
            opt = QuestionOption(question=q, option="option {}".format(i + 1))
            opt.save()
        v = Voting(name="test voting", question=q)
        v.save()

        # Autorizar al votante para votar
        census = Census(voter_id=u.id, voting_id=v.id)
        census.save()

        response = self.client.get(
            "/census/{}/?voter_id={}".format(v.id, u.id), format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), "Valid voter")

    def test_list_voting(self):
        # Crear una votación
        q = Question(desc="test question")
        q.save()
        for i in range(5):
            opt = QuestionOption(question=q, option="option {}".format(i + 1))
            opt.save()
        v = Voting(name="test voting", question=q)
        v.save()

        # Crear un votante
        u, created = User.objects.get_or_create(username='testvoter')
        u.is_active = True
        u.save()

        # Crear un censo
        census = Census.objects.create(voting_id=v.id, voter_id=u.id)

        self.login()
        response = self.client.get("/census/?voting_id={}".format(v.id), format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"voters": [u.id]})

    def test_add_new_voters_conflict(self):
        # Crear una votación
        q = Question(desc="test question")
        q.save()
        for i in range(5):
            opt = QuestionOption(question=q, option="option {}".format(i + 1))
            opt.save()
        v = Voting(name="test voting", question=q)
        v.save()

        # Crear un votante
        u, created = User.objects.get_or_create(username='testvoter')
        u.is_active = True
        u.save()

        # Crear un censo
        census = Census.objects.create(voting_id=v.id, voter_id=u.id)

        self.login()
        data = {"voting_id": v.id, "voters": [u.id]}
        response = self.client.post("/census/", data, format="json")
        self.assertEqual(response.status_code, 409)

    def test_add_new_voters(self):
        # Crear una votación
        q = Question(desc="test question")
        q.save()
        for i in range(5):
            opt = QuestionOption(question=q, option="option {}".format(i + 1))
            opt.save()
        v = Voting(name="test voting", question=q)
        v.save()

        # Crear un votante
        u, created = User.objects.get_or_create(username='testvoter2')
        u.is_active = True
        u.save()

        self.login()
        data = {"voting_id": v.id, "voters": [u.id]}
        response = self.client.post("/census/", data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(data.get("voters")), Census.objects.count()-1)

    def test_destroy_voter(self):
        # Eliminar todos los objetos Census existentes
        Census.objects.all().delete()

        # Crear un votante
        u, created = User.objects.get_or_create(username='testvoter')
        u.is_active = True
        u.save()

        # Crear una votación
        q = Question(desc="test question")
        q.save()
        for i in range(5):
            opt = QuestionOption(question=q, option="option {}".format(i + 1))
            opt.save()
        v = Voting(name="test voting", question=q)
        v.save()

        # Agregar el votante al censo
        census = Census(voter_id=u.id, voting_id=v.id)
        census.save()

        census_to_delete = Census.objects.get(voter_id=u.id, voting_id=v.id)
        deletion = census_to_delete.delete()

        self.assertEqual(deletion[0], 1)  # Comprobar que se eliminó un objeto
        self.assertEqual(0, Census.objects.count())  # Comprobar que no hay objetos Census

class CensusTest(StaticLiveServerTestCase):
    def setUp(self):
        # Load base test functionality for decide
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

    def createCensusSuccess(self):
        self.cleaner.get(self.live_server_url + "/admin/login/?next=/admin/")
        self.cleaner.set_window_size(1280, 720)

        self.cleaner.find_element(By.ID, "id_username").click()
        self.cleaner.find_element(By.ID, "id_username").send_keys("decide")

        self.cleaner.find_element(By.ID, "id_password").click()
        self.cleaner.find_element(By.ID, "id_password").send_keys("decide")

        self.cleaner.find_element(By.ID, "id_password").send_keys("Keys.ENTER")

        self.cleaner.get(self.live_server_url + "/admin/census/census/add")
        now = datetime.now()
        self.cleaner.find_element(By.ID, "id_voting_id").click()
        self.cleaner.find_element(By.ID, "id_voting_id").send_keys(
            now.strftime("%m%d%M%S")
        )
        self.cleaner.find_element(By.ID, "id_voter_id").click()
        self.cleaner.find_element(By.ID, "id_voter_id").send_keys(
            now.strftime("%m%d%M%S")
        )
        self.cleaner.find_element(By.NAME, "_save").click()

        self.assertTrue(
            self.cleaner.current_url == self.live_server_url + "/admin/census/census"
        )

    def createCensusEmptyError(self):
        self.cleaner.get(self.live_server_url + "/admin/login/?next=/admin/")
        self.cleaner.set_window_size(1280, 720)

        self.cleaner.find_element(By.ID, "id_username").click()
        self.cleaner.find_element(By.ID, "id_username").send_keys("decide")

        self.cleaner.find_element(By.ID, "id_password").click()
        self.cleaner.find_element(By.ID, "id_password").send_keys("decide")

        self.cleaner.find_element(By.ID, "id_password").send_keys("Keys.ENTER")

        self.cleaner.get(self.live_server_url + "/admin/census/census/add")

        self.cleaner.find_element(By.NAME, "_save").click()

        self.assertTrue(
            self.cleaner.find_element_by_xpath(
                "/html/body/div/div[3]/div/div[1]/div/form/div/p"
            ).text
            == "Please correct the errors below."
        )
        self.assertTrue(
            self.cleaner.current_url
            == self.live_server_url + "/admin/census/census/add"
        )

    def createCensusValueError(self):
        self.cleaner.get(self.live_server_url + "/admin/login/?next=/admin/")
        self.cleaner.set_window_size(1280, 720)

        self.cleaner.find_element(By.ID, "id_username").click()
        self.cleaner.find_element(By.ID, "id_username").send_keys("decide")

        self.cleaner.find_element(By.ID, "id_password").click()
        self.cleaner.find_element(By.ID, "id_password").send_keys("decide")

        self.cleaner.find_element(By.ID, "id_password").send_keys("Keys.ENTER")

        self.cleaner.get(self.live_server_url + "/admin/census/census/add")
        now = datetime.now()
        self.cleaner.find_element(By.ID, "id_voting_id").click()
        self.cleaner.find_element(By.ID, "id_voting_id").send_keys("64654654654654")
        self.cleaner.find_element(By.ID, "id_voter_id").click()
        self.cleaner.find_element(By.ID, "id_voter_id").send_keys("64654654654654")
        self.cleaner.find_element(By.NAME, "_save").click()

        self.assertTrue(
            self.cleaner.find_element_by_xpath(
                "/html/body/div/div[3]/div/div[1]/div/form/div/p"
            ).text
            == "Please correct the errors below."
        )
        self.assertTrue(
            self.cleaner.current_url
            == self.live_server_url + "/admin/census/census/add"
        )


class CensusExportViewTest(BaseTestCase):
    def setUp(self):
        super().setUp()

    def create_voting(self):
        q = Question(desc="test question")
        q.save()
        for i in range(5):
            opt = QuestionOption(question=q, option="option {}".format(i + 1))
            opt.save()
        v = Voting(name="test voting", question=q)
        v.save()

        a, _ = Auth.objects.get_or_create(
            url=settings.BASEURL, defaults={"me": True, "name": "test auth"}
        )
        a.save()
        v.auths.add(a)

        return v

    def test_census_export_view(self):
        self.create_voting()

        url = reverse("export_census")

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.assertTrue("votings" in response.context)

        votings = response.context["votings"]
        self.assertEqual(votings.count(), Voting.objects.count())

        self.assertTemplateUsed(response, "census/export_census.html")


class ExportCensusTest(BaseTestCase):
    def setUp(self):
        super().setUp()

    def create_voting(self):
        q = Question(desc="test question")
        q.save()
        for i in range(5):
            opt = QuestionOption(question=q, option="option {}".format(i + 1))
            opt.save()
        v = Voting(name="test voting", question=q)
        v.save()

        a, _ = Auth.objects.get_or_create(
            url=settings.BASEURL, defaults={"me": True, "name": "test auth"}
        )
        a.save()
        v.auths.add(a)

        return v

    def create_voters(self, v):
        for i in range(100):
            u, _ = User.objects.get_or_create(username="testvoter{}".format(i))
            u.is_active = True
            u.save()
            c = Census(voter_id=u.id, voting_id=v.id)
            c.save()

    def test_export_census(self):
        v = self.create_voting()
        self.create_voters(v)

        url = reverse("export_census_of_voting", args=[v.id])

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            response["Content-Type"],
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

        self.assertEqual(
            response["Content-Disposition"], "attachment; filename=census.xlsx"
        )

        workbook = load_workbook(BytesIO(response.content))
        worksheet = workbook.active

        self.assertEqual(worksheet["A1"].value, f"Census for: {v.name}")

        self.assertEqual(worksheet["A2"].value, "Voting ID")
        self.assertEqual(worksheet["B2"].value, "Voter ID")

        census_data = Census.objects.filter(voting_id=v.id)
        for i, row in enumerate(census_data, start=3):
            self.assertEqual(worksheet[f"A{i}"].value, row.voting_id)
            self.assertEqual(worksheet[f"B{i}"].value, row.voter_id)



class CensusImportViewTest(BaseTestCase):
    def setUp(self):
        super().setUp()

    def create_voting(self):
        q = Question(desc="test question")
        q.save()
        for i in range(5):
            opt = QuestionOption(question=q, option="option {}".format(i + 1))
            opt.save()
        v = Voting(name="test voting", question=q)
        v.save()

        a, _ = Auth.objects.get_or_create(
            url=settings.BASEURL, defaults={"me": True, "name": "test auth"}
        )
        a.save()
        v.auths.add(a)

        return v