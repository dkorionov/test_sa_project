from details.services import PlannedDetailAllocationService, PlannedDetailDAO
from django.core.management import BaseCommand
from tasks.models import Task
from tasks.services import TaskDAO, TaskService


class Command(BaseCommand):
    help = 'Allocate planned details between tasks'

    def handle(self, *args, **options):
        tasks = Task.objects.filter(status__in=[Task.Status.TODO, Task.Status.IN_PROGRESS]).order_by("expected_date")
        task_service = TaskService(
            task_dao=TaskDAO(),
            planned_detail_allocation_service=PlannedDetailAllocationService(),
            planned_detail_dao=PlannedDetailDAO(),
        )
        task_service.allocate_task_list(tasks)
