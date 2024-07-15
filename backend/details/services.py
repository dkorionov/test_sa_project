import logging
from typing import Iterable

from details.exceptions import NotEnoughDetail
from details.models import Detail, DetailInStock, PlannedDetail
from django.db import transaction
from django.db.models import F, QuerySet, Sum
from sa_project.services.base_dao import BaseDao
from sa_project.services.helpers import prefetch_related

__all__ = ['DetailDAO', 'PlannedDetailDAO', 'DetailInStockDAO', 'PlannedDetailAllocationService']

from tasks.models import Task

logger = logging.getLogger(__name__)


class DetailDAO(BaseDao):
    model = Detail

    @prefetch_related(['similar_details'])
    def get_all_details_with_similar_details(self) -> QuerySet[Detail]:
        return self.model.objects.all()


class PlannedDetailDAO(BaseDao):
    model = PlannedDetail

    @staticmethod
    def get_planned_details_from_task(task: Task) -> QuerySet[PlannedDetail]:
        return (
            task.planned_details.filter(quantity_in_stock__lt=F('planned_quantity'))
            .select_related('detail')
        ).select_for_update()


class DetailInStockDAO(BaseDao):
    model = DetailInStock


class PlannedDetailAllocationService:
    """
    Service for handling the allocation of planned details from stock.
    """

    def allocated_batch_planned_details(
            self,
            planned_details: Iterable[PlannedDetail],
            allocate_from_using_similar: bool = True,
            raise_not_enough: bool = False,
    ):
        """
        Allocate a list of planned details from stock.
        """
        with transaction.atomic():
            for planned_detail in planned_details:
                self.allocate_planned_detail(planned_detail, allocate_from_using_similar, raise_not_enough)

    def allocate_planned_detail(
            self,
            planned_detail: PlannedDetail,
            allocate_from_using_similar: bool = True,
            raise_not_enough: bool = False,
    ):
        """
        Allocate a single planned detail from stock.
        """

        # can't prefetch select for update
        details_in_stock = (
            DetailInStock.objects.filter(detail=planned_detail.detail)
            .filter(quantity__gt=0)
            .only('quantity')
            .select_for_update()
        )

        # Allocate from stock
        to_update_details_in_stock = self._allocate_from_stock(
            planned_detail,
            details_in_stock,
        )

        # Allocate using similar details
        if allocate_from_using_similar and planned_detail.quantity_in_stock < planned_detail.planned_quantity:
            self._allocate_using_similar_details(planned_detail, to_update_details_in_stock)

        # Check if there are enough details in stock
        if raise_not_enough and planned_detail.quantity_in_stock < planned_detail.planned_quantity:
            raise NotEnoughDetail(
                planned_detail_id=planned_detail.id,
                detail_id=int(planned_detail.detail_id),
                required_quantity=planned_detail.planned_quantity,
                in_stock_quantity=planned_detail.quantity_in_stock,
            )

        planned_detail.save(update_fields=['quantity_in_stock'])
        DetailInStock.objects.bulk_update(to_update_details_in_stock, ['quantity'])

    def _allocate_using_similar_details(
            self,
            planned_detail: PlannedDetail,
            to_update_details_in_stock: list[DetailInStock],
    ):
        """
        Allocate details using similar details in stock.
        """
        similar_detail_ids = planned_detail.detail.similar_details.values_list('id', flat=True)

        # can't prefetch select for update
        similar_details_in_stock = DetailInStock.objects.filter(
            detail__id__in=similar_detail_ids,
            quantity__gt=0,
        ).only('quantity').select_for_update()

        to_update_details_in_stock.extend(
            self._allocate_from_stock(planned_detail, similar_details_in_stock),
        )

    @staticmethod
    def _allocate_from_stock(
            planned_detail: PlannedDetail,
            in_stock: Iterable[DetailInStock],
    ) -> list[DetailInStock]:
        """
        Allocate the required quantity from stock.
        """
        updated_details_in_stock = []
        total_allocated_pcs = planned_detail.quantity_in_stock
        need_to_allocate_pcs = planned_detail.planned_quantity

        for detail_in_stock in in_stock:
            if total_allocated_pcs < need_to_allocate_pcs:
                alloc_pcs = min(detail_in_stock.quantity, need_to_allocate_pcs - total_allocated_pcs)
                # Allocate the required quantity
                detail_in_stock.quantity -= alloc_pcs
                total_allocated_pcs += alloc_pcs
                updated_details_in_stock.append(detail_in_stock)

        # Update the quantity in stock for the planned detail
        planned_detail.quantity_in_stock = total_allocated_pcs
        return updated_details_in_stock

    def is_enough_details_in_stock(self, planned_detail: PlannedDetail) -> bool:
        """
        Check if there are enough details in stock for the planned detail.
        """
        return planned_detail.planned_quantity <= self.get_total_quantity_in_stock(planned_detail)

    def can_full_allocate(self, planned_details: Iterable[PlannedDetail]) -> bool:
        """
        Check if list of planned details can be fully allocated from stock.
        """

        return all(self.is_enough_details_in_stock(planned_detail) for planned_detail in planned_details)

    @staticmethod
    def get_total_quantity_in_stock_batch(
            planned_details: Iterable[PlannedDetail],
            using_similar: bool = True,
    ) -> int:
        """
        Get the total quantity in stock for a list of planned details.
        """
        detail_ids = []
        for planned_detail in planned_details:
            detail_ids.append(planned_detail.detail_id)
            if using_similar:
                detail_ids.extend(list(planned_detail.detail.similar_details.values_list('id', flat=True)))

        total_quantity = DetailInStock.objects.filter(
            detail_id__in=detail_ids,
            quantity__gt=0,
        ).aggregate(total_quantity=Sum("quantity"))

        return total_quantity.get("total_quantity") or 0

    @staticmethod
    def get_total_quantity_in_stock(planned_detail: PlannedDetail, using_similar: bool = True) -> int:
        """
        Get the total quantity in stock for a planned detail.
        """
        detail_ids = [planned_detail.detail_id]
        if using_similar:
            detail_ids = list(planned_detail.detail.similar_details.values_list("id", flat=True))

        total_quantity = DetailInStock.objects.filter(
            detail_id__in=detail_ids,
            quantity__gt=0,
        ).aggregate(total_quantity=Sum("quantity"))

        return total_quantity.get("total_quantity") or 0
