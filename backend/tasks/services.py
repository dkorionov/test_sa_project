from typing import Iterable

from details.services import PlannedDetailAllocationService, PlannedDetailDAO
from django.contrib.auth.models import User
from django.db.models import QuerySet
from sa_project.services.base_dao import BaseDao
from sa_project.services.helpers import prefetch_related
from tasks.models import Task

__all__ = ['TaskDAO', 'TaskService']


class TaskDAO(BaseDao):
    model = Task

    @prefetch_related(['planned_details'])
    def get_all_task_with_planned_details(self, user: User) -> QuerySet[Task]:
        return self.model.objects.filter(author=user)

    @staticmethod
    def _change_status(task: Task, status: Task.Status):
        if status != task.status:
            task.status = status
            task.save(update_fields=['status'])

    def change_to_in_progress(self, task: Task):
        self._change_status(task, Task.Status.IN_PROGRESS)

    def change_to_review(self, task: Task):
        self._change_status(task, Task.Status.REVIEW)

    def change_to_completed(self, task: Task):
        self._change_status(task, Task.Status.COMPLETED)


class TaskService:

    def __init__(
            self,
            task_dao: TaskDAO,
            planned_detail_allocation_service: PlannedDetailAllocationService,
            planned_detail_dao: PlannedDetailDAO,
    ):
        self.task_dao = task_dao
        self.planned_detail_allocation_service = planned_detail_allocation_service
        self.planned_detail_dao = planned_detail_dao

    def allocate_task(
            self,
            task: Task,
    ):
        """
        Allocate a task with details from stock.

        """
        planned_details = self.planned_detail_dao.get_planned_details_from_task(task)
        task.status = Task.Status.IN_PROGRESS
        task.save(update_fields=['status'])
        if self.planned_detail_allocation_service.can_full_allocate(planned_details):
            self.planned_detail_allocation_service.allocated_batch_planned_details(planned_details)
            task.status = Task.Status.COMPLETED
            task.save(update_fields=['status'])
        else:
            self.planned_detail_allocation_service.allocated_batch_planned_details(planned_details)

    def allocate_task_list(self, tasks: Iterable[Task]):
        """
        Allocate a list of tasks with details from stock.
        Tasks that can be fully allocated are handled first.
        """
        tasks_to_update = []
        tasks_to_allocate_partially = []

        # Allocate fully allocatable tasks
        for task in tasks:
            planned_details = self.planned_detail_dao.get_planned_details_from_task(task)
            task.status = Task.Status.IN_PROGRESS
            task.save(update_fields=['status'])
            if self.planned_detail_allocation_service.can_full_allocate(planned_details):
                self.planned_detail_allocation_service.allocated_batch_planned_details(planned_details)
                task.status = Task.Status.COMPLETED
                tasks_to_update.append(task.id)
            else:
                tasks_to_allocate_partially.append((task, planned_details))

        # Allocate remaining tasks
        for task, planned_details in tasks_to_allocate_partially:
            self.planned_detail_allocation_service.allocated_batch_planned_details(planned_details)

        # Update status of fully allocated tasks to COMPLETED
        if tasks_to_update:
            Task.objects.filter(id__in=tasks_to_update).update(status=Task.Status.COMPLETED)
