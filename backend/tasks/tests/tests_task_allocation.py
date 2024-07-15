from details.services import PlannedDetailAllocationService, PlannedDetailDAO
from details.tests.factories import (
    DetailFactory, DetailInStockFactory,
    PlannedDetailFactory,
    TestDetailDataGenerator, WareHouseFactory,
)
from django.db import connection
from django.test.utils import CaptureQueriesContext
from rest_framework.test import APITestCase
from tasks.models import Task
from tasks.services import TaskDAO, TaskService
from tasks.tests.factories import TaskFactory, UserFactory


class TestTaskAllocation(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.detail_allocation_service = PlannedDetailAllocationService()
        cls.planned_detail_dao = PlannedDetailDAO()
        cls.task_dao = TaskDAO()
        cls.task_service = TaskService(
            task_dao=cls.task_dao,
            planned_detail_allocation_service=cls.detail_allocation_service,
            planned_detail_dao=cls.planned_detail_dao,
        )
        cls.data_generator = TestDetailDataGenerator(
            user_factory=UserFactory,
            task_factory=TaskFactory,
            detail_factory=DetailFactory,
            warehouse_factory=WareHouseFactory,
            planned_detail_factory=PlannedDetailFactory,
            detail_in_stock_factory=DetailInStockFactory,
        )
        cls.data_generator.generate_test_data()

    def test_allocate_full_single_task(self):
        task = Task.objects.first()
        self.assertEqual(task.status, Task.Status.TODO)
        with CaptureQueriesContext(connection):
            self.task_service.allocate_task(task)
        task.refresh_from_db()
        self.assertEqual(task.status, Task.Status.COMPLETED)

    def test_allocate_partially_single_task(self):
        task = Task.objects.first()
        task.planned_details.update(planned_quantity=100)
        self.assertEqual(task.status, Task.Status.TODO)
        with CaptureQueriesContext(connection):
            self.task_service.allocate_task(task)
        task.refresh_from_db()
        self.assertEqual(task.status, Task.Status.IN_PROGRESS)

    def test_allocate_task_list(self):
        tasks = Task.objects.filter(status__in=[Task.Status.TODO, Task.Status.IN_PROGRESS]).order_by("expected_date")
        self.assertEqual(tasks.count(), 3)
        self.assertEqual(tasks.filter(status=Task.Status.TODO).count(), 3)
        with CaptureQueriesContext(connection):
            self.task_service.allocate_task_list(tasks)
        tasks = Task.objects.all()
        self.assertEqual(tasks.filter(status=Task.Status.COMPLETED).count(), 1)
        self.assertEqual(tasks.filter(status=Task.Status.IN_PROGRESS).count(), 2)
