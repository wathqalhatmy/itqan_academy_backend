from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from apps.halaqat.models import Circle, Student, Attendance, MemorizationRecord, JuzTest

class HalaqatModularApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='password123')
        
        # Authenticate client
        response = self.client.post('/api/v1/auth/login/', {'username': 'testuser', 'password': 'password123'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        # Create base test models
        self.circle = Circle.objects.create(name='حلقة الفجر', teacher_name='الشيخ أحمد', level='memorization')
        self.student = Student.objects.create(
            name='محمد علي',
            circle=self.circle,
            status='active',
            behavior_rating=4.5,
            completed_juz=[1, 2, 3]
        )

    def test_circle_crud_and_student_removal(self):
        response = self.client.get('/api/v1/halaqat/circles/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.post(f'/api/v1/halaqat/circles/{self.circle.id}/remove-student/', {'student_id': self.student.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.student.refresh_from_db()
        self.assertIsNone(self.student.circle)

    def test_attendance_bulk_save_success(self):
        bulk_data = [
            {
                'studentId': self.student.id,
                'circleId': self.circle.id,
                'date': '2026-07-23T10:00:00Z',
                'status': 'present',
                'note': 'حضور ممتاز'
            }
        ]
        response = self.client.post('/api/v1/halaqat/attendance/bulk-save/', bulk_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Attendance.objects.count(), 1)
