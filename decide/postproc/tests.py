from django.test import TestCase

from rest_framework.test import APIClient
from rest_framework.test import APITestCase

from base import mods


class PostProcTestCase(APITestCase):
    """
    Test case for the PostProc API endpoint.

    This test case covers the behavior of the PostProc API endpoint, which performs post-processing on voting results.

    :ivar client: The Django REST framework API client.
    :vartype client: APIClient
    """

    def setUp(self):
        """
        Set up the test environment before each test method is run.

        This method is called before each test method in the test case.

        :return: None
        """
        self.client = APIClient()
        mods.mock_query(self.client)

    def tearDown(self):
        """
        Clean up the test environment after each test method is run.

        This method is called after each test method in the test case.

        :return: None
        """
        self.client = None

    def test_identity(self):
        """
        Test the behavior of the PostProc API endpoint with the 'IDENTITY' type.

        This test sends a POST request to the '/postproc/' endpoint with identity-type data and verifies
        that the response contains the expected post-processed result.

        :return: None
        """
        data = {
            'type': 'IDENTITY',
            'options': [
                {'option': 'Option 1', 'number': 1, 'votes': 5},
                {'option': 'Option 2', 'number': 2, 'votes': 0},
                {'option': 'Option 3', 'number': 3, 'votes': 3},
                {'option': 'Option 4', 'number': 4, 'votes': 2},
                {'option': 'Option 5', 'number': 5, 'votes': 5},
                {'option': 'Option 6', 'number': 6, 'votes': 1},
            ]
        }

        expected_result = [
            {'option': 'Option 1', 'number': 1, 'votes': 5, 'postproc': 5},
            {'option': 'Option 5', 'number': 5, 'votes': 5, 'postproc': 5},
            {'option': 'Option 3', 'number': 3, 'votes': 3, 'postproc': 3},
            {'option': 'Option 4', 'number': 4, 'votes': 2, 'postproc': 2},
            {'option': 'Option 6', 'number': 6, 'votes': 1, 'postproc': 1},
            {'option': 'Option 2', 'number': 2, 'votes': 0, 'postproc': 0},
        ]

        response = self.client.post('/postproc/', data, format='json')
        self.assertEqual(response.status_code, 200)

        values = response.json()
        self.assertEqual(values, expected_result)
