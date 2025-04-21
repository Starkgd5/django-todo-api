from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from .models import Tag, Todo

User = get_user_model()


class TodoAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.tag1 = Tag.objects.create(name='Work', color='#FF0000')
        self.tag2 = Tag.objects.create(name='Personal', color='#00FF00')

        self.todo1 = Todo.objects.create(
            title='Finish project',
            description='Complete the DRF project',
            priority=3,
            user=self.user
        )
        self.todo1.tags.add(self.tag1)

        self.todo2 = Todo.objects.create(
            title='Buy groceries',
            description='Milk, eggs, bread',
            priority=2,
            status='completed',
            user=self.user
        )
        self.todo2.tags.add(self.tag2)

    def test_create_todo(self):
        url = reverse('todo-list')
        data = {
            'title': 'New Task',
            'description': 'New description',
            'priority': 1,
            'tags': [
                {'name': 'Work', 'color': '#FF0000'},
                {'name': 'Urgent', 'color': '#FF0000'}
            ]
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Todo.objects.count(), 3)
        # Should create the 'Urgent' tag
        self.assertEqual(Tag.objects.count(), 3)

    def test_get_todos(self):
        url = reverse('todo-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_filter_todos(self):
        url = reverse('todo-list')
        response = self.client.get(url, {'priority': 3})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results']
                         [0]['title'], 'Finish project')

    def test_update_status(self):
        url = reverse('todo-update-status', kwargs={'pk': self.todo1.pk})
        data = {'status': 'in_progress'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.todo1.refresh_from_db()
        self.assertEqual(self.todo1.status, 'in_progress')

    def test_completed_action(self):
        url = reverse('todo-completed')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Buy groceries')

    def test_tag_list(self):
        url = reverse('tag-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_unauthenticated_access(self):
        self.client.logout()
        url = reverse('todo-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class PaginationTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='paginationuser',
            email='pagination@example.com',
            password='testpass123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        # Create more than 10 todos to test pagination
        for i in range(15):
            Todo.objects.create(
                title=f'Task {i}',
                description=f'Description {i}',
                priority=1,
                user=self.user
            )

    def test_pagination(self):
        url = reverse('todo-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 10)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
        self.assertEqual(response.data['count'], 15)
