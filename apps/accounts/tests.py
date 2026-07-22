from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status

class AccountsApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='teacher1', password='password123')

    def test_login_and_current_user(self):
        response = self.client.post('/api/v1/auth/login/', {'username': 'teacher1', 'password': 'password123'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        token = response.data['access']
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        res_me = self.client.get('/api/v1/auth/me/')
        self.assertEqual(res_me.status_code, status.HTTP_200_OK)
        self.assertEqual(res_me.data['username'], 'teacher1')
