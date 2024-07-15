import json

from details.models import Detail, PlannedDetail
from details.serializers import (
    BasePlannedDetailSerializer,
    CreateDetailSerializer,
)
from details.tests.factories import TestDetailDataGenerator
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from tasks.models import Task


class TestDetailAPI(APITestCase):

    def setUp(self):
        self.user = User.objects.first()
        self.client.force_authenticate(self.user)

    @classmethod
    def setUpTestData(cls):
        cls.test_data_generator = TestDetailDataGenerator()
        cls.test_data_generator.generate_test_data()
        cls.list_create_detail_view_name = 'list-create-detail'
        cls.retrieve_update_destroy_detail_view_name = 'retrieve-update-destroy-detail'

    def test_create_detail(self):
        response = self.client.post(
            reverse(self.list_create_detail_view_name),
            data={
                'name': 'test detail',
                'description': 'test description',
                "unit_of_measurement": "pcs",
                "price_for_unit": 100,
            },
        )
        self.assertEqual(response.status_code, 201)
        new_detail = Detail.objects.last()
        serialized_data = CreateDetailSerializer(new_detail).data
        self.assertEqual(json.dumps(serialized_data), json.dumps(response.data))

    def test_get_detail_list(self):
        response = self.client.get(reverse(self.list_create_detail_view_name))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data.get("results", [])), Detail.objects.count())

    def test_get_detail(self):
        detail = Detail.objects.first()
        response = self.client.get(reverse(self.retrieve_update_destroy_detail_view_name, kwargs={'pk': detail.id}))
        self.assertEqual(response.status_code, 200)

    def test_update_detail(self):
        detail = Detail.objects.first()
        new_name = 'new name'
        response = self.client.patch(
            reverse(self.retrieve_update_destroy_detail_view_name, kwargs={'pk': detail.id}),
            data={'name': new_name},
        )
        self.assertEqual(response.status_code, 200)
        detail.refresh_from_db()
        self.assertEqual(detail.name, new_name)

    def test_delete_detail(self):
        detail = Detail.objects.first()
        response = self.client.delete(
            reverse(self.retrieve_update_destroy_detail_view_name, kwargs={'pk': detail.id}),
        )
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Detail.objects.filter(id=detail.id).exists())


class TestPlannedDetailAPI(APITestCase):

    def setUp(self):
        self.user = User.objects.first()
        self.client.force_authenticate(self.user)

    @classmethod
    def setUpTestData(cls):
        cls.test_data_generator = TestDetailDataGenerator()
        cls.test_data_generator.generate_test_data()
        cls.list_create_planned_details_view_name = 'list-create-planned-detail'
        cls.retrieve_update_delete_planned_detail_view_name = 'retrieve-update-destroy-planned-detail'

    def test_create_planned_detail(self):
        response = self.client.post(
            reverse(self.list_create_planned_details_view_name),
            data={
                'detail': Detail.objects.first().id,
                'planned_quantity': 100,
                'task': Task.objects.first().id,
            },
        )
        self.assertEqual(response.status_code, 201)
        serialized_data = BasePlannedDetailSerializer(PlannedDetail.objects.last()).data
        self.assertEqual(serialized_data, response.data)

    def test_get_planned_detail_list(self):
        response = self.client.get(reverse(self.list_create_planned_details_view_name))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data.get("results", [])), PlannedDetail.objects.count())

    def test_get_planned_detail(self):
        planned_detail = PlannedDetail.objects.first()
        response = self.client.get(
            reverse(self.retrieve_update_delete_planned_detail_view_name, kwargs={'pk': planned_detail.id}),
        )
        self.assertEqual(response.status_code, 200)

    def test_update_planned_detail(self):
        planned_detail = PlannedDetail.objects.first()
        response = self.client.patch(
            reverse(self.retrieve_update_delete_planned_detail_view_name, kwargs={'pk': planned_detail.id}),
            data={'planned_quantity': 200},
        )
        self.assertEqual(response.status_code, 200)
        planned_detail.refresh_from_db()
        self.assertEqual(planned_detail.planned_quantity, 200)

    def test_delete_planned_detail(self):
        planned_detail = PlannedDetail.objects.first()
        response = self.client.delete(
            reverse(self.retrieve_update_delete_planned_detail_view_name, kwargs={'pk': planned_detail.id}),
        )
        self.assertEqual(response.status_code, 204)
