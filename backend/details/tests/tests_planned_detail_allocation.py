from details.models import DetailInStock, PlannedDetail
from details.services import PlannedDetailAllocationService, PlannedDetailDAO
from details.tests.factories import (
    DetailFactory, DetailInStockFactory,
    PlannedDetailFactory,
    TestDetailDataGenerator, WareHouseFactory,
)
from django.db import connection
from django.db.models import Sum
from django.test.utils import CaptureQueriesContext
from rest_framework.test import APITestCase
from tasks.models import Task
from tasks.tests.factories import TaskFactory, UserFactory


class TestDetailAllocation(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.detail_allocation_service = PlannedDetailAllocationService()
        cls.planned_detail_dao = PlannedDetailDAO()
        cls.data_generator = TestDetailDataGenerator(
            user_factory=UserFactory,
            task_factory=TaskFactory,
            detail_factory=DetailFactory,
            warehouse_factory=WareHouseFactory,
            planned_detail_factory=PlannedDetailFactory,
            detail_in_stock_factory=DetailInStockFactory,
        )
        cls.data_generator.generate_test_data()

    @staticmethod
    def get_quantity_in_stock(planned_detail: PlannedDetail) -> int:
        similar_details = list(planned_detail.detail.similar_details.all())
        similar_details.append(planned_detail.detail)
        pcs_in_stocks = int(
            DetailInStock.objects.filter(detail__in=similar_details)
            .aggregate(Sum('quantity'))['quantity__sum'],
        )
        return pcs_in_stocks

    def full_allocate_task(self, task: Task):
        planned_details = self.planned_detail_dao.get_planned_details_from_task(task)
        self.assertTrue(self.detail_allocation_service.can_full_allocate(planned_details))

        initial_total_quantity = (
            self.detail_allocation_service.
            get_total_quantity_in_stock_batch(planned_details)
        )

        with CaptureQueriesContext(connection):
            self.detail_allocation_service.allocated_batch_planned_details(
                planned_details,
            )

        new_total_quantity = (
            self.detail_allocation_service.
            get_total_quantity_in_stock_batch(planned_details)
        )

        allocated_details_pcs = 0
        for planned_detail in planned_details:
            allocated_details_pcs += planned_detail.quantity_in_stock
            self.assertEqual(planned_detail.quantity_in_stock, planned_detail.planned_quantity)
        self.assertEqual(initial_total_quantity, new_total_quantity + allocated_details_pcs)

    def partial_allocate_task(self, task: Task):
        planned_details = self.planned_detail_dao.get_planned_details_from_task(task)
        self.assertFalse(self.detail_allocation_service.can_full_allocate(planned_details))
        initial_total_quantity = (
            self.detail_allocation_service.
            get_total_quantity_in_stock_batch(task.planned_details.all())
        )

        with CaptureQueriesContext(connection):
            self.detail_allocation_service.allocated_batch_planned_details(planned_details)

        new_total_quantity = (
            self.detail_allocation_service.
            get_total_quantity_in_stock_batch(task.planned_details.all())
        )
        allocated_details_pcs = 0
        for planned_detail in planned_details:
            allocated_details_pcs += planned_detail.quantity_in_stock

        self.assertEqual(initial_total_quantity, new_total_quantity + allocated_details_pcs)

    def test_task_allocation(self):
        tasks = Task.objects.all()
        self.full_allocate_task(tasks[0])
        self.partial_allocate_task(tasks[1])
        self.partial_allocate_task(tasks[2])
