from django.test import TestCase
from base.tests import BaseTestCase


# Create your tests here.

class BoothTestCase(BaseTestCase):
    """
    Test case for the BoothView in the booth app.

    This test case includes methods to test the behavior of the BoothView under different scenarios.

    :ivar client: The Django test client used to simulate HTTP requests.
    :vartype client: Client
    """
    def setUp(self):
        """
        Set up the test environment before each test method is run.

        This method is called before each test method in the test case.

        :return: None
        """
        super().setUp()
    def tearDown(self):
        """
        Clean up the test environment after each test method is run.

        This method is called after each test method in the test case.

        :return: None
        """

        super().tearDown()
    def testBoothNotFound(self):
        """
        Test the behavior when trying to access a non-existing booth.

        The view should return a 404 status code when attempting to access a booth
        with a voting ID that does not exist.

        :return: None
        """
        response = self.client.get('/booth/10000/')
        self.assertEqual(response.status_code, 404)
    
    def testBoothRedirection(self):
        """
        Test the behavior when accessing a booth without a trailing slash.

        The view should return a 301 (permanent redirect) status code when accessing a booth
        with a voting ID without a trailing slash.

        :return: None
        """   
        response = self.client.get('/booth/10000')
        self.assertEqual(response.status_code, 301)

       