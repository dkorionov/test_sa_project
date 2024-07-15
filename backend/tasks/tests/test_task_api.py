import json

from details.tests.factories import TestDetailDataGenerator
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase
from tasks.models import Task

from .factories import TaskFactory, UserFactory


class TestTaskAPI(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.task_factory = TaskFactory
        cls.user_factory = UserFactory
        cls.test_data_generator = TestDetailDataGenerator()
        cls.test_data_generator.generate_test_data()
        cls.list_create_view_name = 'list-create-task'
        cls.retrieve_update_delete_task_view_name = 'retrieve-update-delete-task'
        cls.update_to_review_view_name = 'update-to-review'

    def test_get_task_list_un_auth(self):
        response = self.client.get(reverse(self.list_create_view_name))
        self.assertEqual(response.status_code, 401)

    def test_get_task_list(self):
        from tasks.serializers import ListTaskSerializer
        author = User.objects.first()
        self.client.force_authenticate(author)
        response = self.client.get(reverse(self.list_create_view_name))
        tasks = Task.objects.filter(author=author)
        tasks_data = ListTaskSerializer(tasks, many=True).data
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data.get("results", [])), tasks.count())
        self.assertEqual(json.dumps(tasks_data), json.dumps(response.data['results']))

    def test_create_task(self):
        author = User.objects.first()
        self.client.force_authenticate(author)
        task_data = {
            'description': 'test task',
            'expected_date': str(timezone.now().date() + timezone.timedelta(days=1)),
            "executor": User.objects.last().id,
        }

        response = self.client.post(
            reverse(self.list_create_view_name),
            data=task_data,
        )
        self.assertEqual(response.status_code, 201)
        new_task = Task.objects.last()
        self.assertEqual(new_task.id, response.data.get('id'))

    def test_retrieve_task(self):
        author = User.objects.first()
        self.client.force_authenticate(author)
        task = Task.objects.first()
        response = self.client.get(reverse(self.retrieve_update_delete_task_view_name, kwargs={'pk': task.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(task.id, response.data.get('id'))

    def test_update_task_forbidden(self):
        user = User.objects.last()
        self.client.force_authenticate(user)
        task = Task.objects.first()
        self.assertFalse(task.author == user)
        task_data = {
            'description': 'some new description',
        }
        response = self.client.patch(
            reverse(self.retrieve_update_delete_task_view_name, kwargs={'pk': task.id}),
            data=task_data,
        )
        self.assertEqual(response.status_code, 403)

    def test_update_task(self):
        author = User.objects.first()
        self.client.force_authenticate(author)
        task = Task.objects.first()
        task_data = {
            'description': 'some new description',
        }
        response = self.client.patch(
            reverse(self.retrieve_update_delete_task_view_name, kwargs={'pk': task.id}),
            data=task_data,
        )
        self.assertEqual(response.status_code, 200)
        task.refresh_from_db()
        self.assertEqual(task.description, task_data['description'])

    def test_delete_forbidden(self):
        user = User.objects.last()
        self.client.force_authenticate(user)
        task = Task.objects.first()
        self.assertFalse(task.author == user)
        response = self.client.delete(
            reverse(self.retrieve_update_delete_task_view_name, kwargs={'pk': task.id}),
        )
        self.assertEqual(response.status_code, 403)

    def test_delete(self):
        author = User.objects.first()
        self.client.force_authenticate(author)
        task = Task.objects.first()
        response = self.client.delete(
            reverse(self.retrieve_update_delete_task_view_name, kwargs={'pk': task.id}),
        )
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Task.objects.filter(id=task.id).exists())

    def test_change_status_to_review(self):
        author = User.objects.first()
        self.client.force_authenticate(author)
        task = Task.objects.first()
        response = self.client.patch(
            reverse(self.update_to_review_view_name, kwargs={'pk': task.id}),
        )
        self.assertEqual(response.status_code, 200)
        task.refresh_from_db()
        self.assertEqual(task.status, Task.Status.REVIEW)
