from typing import Type

import factory
from details.models import Detail, DetailInStock, PlannedDetail, WareHouse
from django.utils import timezone
from faker import Faker
from tasks.models import Task
from tasks.tests.factories import TaskFactory, UserFactory

fake = Faker()


class DetailFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Detail

    name = factory.Faker('word')
    unit_of_measurement = "pcs"
    price_for_unit = factory.Faker('pydecimal', left_digits=5, right_digits=2, positive=True)

    @factory.post_generation
    def similar_details(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for similar in extracted:
                self.similar_details.add(similar)


class WareHouseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = WareHouse

    name = factory.Faker('company')
    address = factory.Faker('address')
    phone = factory.Faker('phone_number')
    email = factory.Faker('email')


class PlannedDetailFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PlannedDetail

    detail = factory.SubFactory(DetailFactory)
    task = factory.SubFactory(TaskFactory)
    planned_quantity = 0
    quantity_in_stock = 0


class DetailInStockFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DetailInStock

    detail = factory.SubFactory(DetailFactory)
    quantity = 0
    warehouse = factory.SubFactory(WareHouseFactory)


class TestDetailDataGenerator:

    def __init__(
            self,
            user_factory: Type[UserFactory] = UserFactory,
            task_factory: Type[TaskFactory] = TaskFactory,
            detail_factory: Type[DetailFactory] = DetailFactory,
            warehouse_factory: Type[WareHouseFactory] = WareHouseFactory,
            planned_detail_factory: Type[PlannedDetailFactory] = PlannedDetailFactory,
            detail_in_stock_factory: Type[DetailInStockFactory] = DetailInStockFactory,
    ):
        self.user_factory = user_factory
        self.task_factory = task_factory
        self.detail_factory = detail_factory
        self.warehouse_factory = warehouse_factory
        self.planned_detail_factory = planned_detail_factory
        self.detail_in_stock_factory = detail_in_stock_factory

    def _create_tasks(self) -> list[Task]:
        users = self.user_factory.create_batch(3)
        task_1 = self.task_factory.create(
            author=users[0],
            executor=users[1],
            expected_date=timezone.now() + timezone.timedelta(days=1),
        )
        task_2 = self.task_factory.create(
            author=users[0],
            executor=users[2],
            expected_date=timezone.now() + timezone.timedelta(days=1),
        )
        task_3 = self.task_factory.create(
            author=users[0],
            executor=users[1],
            expected_date=timezone.now() + timezone.timedelta(days=2),
        )
        return [task_1, task_2, task_3]

    def _create_details(self) -> list[list["Detail"]]:
        bearing_a = self.detail_factory.create(name="Bearing A")
        bearing_b = self.detail_factory.create(name="Bearing B", similar_details=[bearing_a])
        bearing_c = self.detail_factory.create(name="Bearing C")
        bushing_a = self.detail_factory.create(name="Bushing A")
        bushing_b = self.detail_factory.create(name="Bushing B", similar_details=[bushing_a])
        bushing_c = self.detail_factory.create(name="Bushing C")
        bearings = [bearing_a, bearing_b, bearing_c]
        bushings = [bushing_a, bushing_b, bushing_c]
        return [bearings, bushings]

    def _create_planned_details(self, tasks: list[Task], details: list[list[Detail]]):
        bearing, bushing = details
        self.planned_detail_factory.create(
            task=tasks[0],
            detail=bearing[0],
            planned_quantity=10,
        )
        self.planned_detail_factory.create(
            task=tasks[1],
            detail=bearing[0],
            planned_quantity=10,
        )
        self.planned_detail_factory.create(
            task=tasks[1],
            detail=bushing[0],
            planned_quantity=40,
        )

        self.planned_detail_factory.create(
            task=tasks[2],
            detail=bearing[1],
            planned_quantity=10,
        )
        self.planned_detail_factory.create(
            task=tasks[2],
            detail=bushing[1],
            planned_quantity=40,
        )

    def _create_details_in_stock(self, details: list[list[Detail]], warehouses: list[WareHouse]):
        bearings, bushings = details
        warehouse_1, warehouse_2 = warehouses
        self.detail_in_stock_factory.create(
            detail=bearings[0],
            quantity=1,
            warehouse=warehouse_1,
        )
        self.detail_in_stock_factory.create(
            detail=bearings[0],
            quantity=1,
            warehouse=warehouse_2,
        )
        self.detail_in_stock_factory.create(
            detail=bearings[1],
            quantity=5,
            warehouse=warehouse_1,
        )
        self.detail_in_stock_factory.create(
            detail=bearings[1],
            quantity=5,
            warehouse=warehouse_2,
        )

        self.detail_in_stock_factory.create(
            detail=bushings[0],
            quantity=10,
            warehouse=warehouse_1,
        )
        self.detail_in_stock_factory.create(
            detail=bushings[0],
            quantity=10,
            warehouse=warehouse_2,
        )

        self.detail_in_stock_factory.create(
            detail=bushings[1],
            quantity=20,
            warehouse=warehouse_1,
        )

        self.detail_in_stock_factory.create(
            detail=bushings[1],
            quantity=20,
            warehouse=warehouse_2,
        )

    def generate_test_data(self):
        tasks = self._create_tasks()
        details = self._create_details()
        warehouse_1 = self.warehouse_factory.create()
        warehouse_2 = self.warehouse_factory.create()
        self._create_planned_details(tasks, details)
        self._create_details_in_stock(details, [warehouse_1, warehouse_2])
