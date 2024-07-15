class NotEnoughDetail(Exception):

    def __init__(
            self,
            planned_detail_id: int,
            detail_id: int,
            required_quantity: int,
            in_stock_quantity: int,
    ):
        self.message = "Not enough detail in stock"
        self.planned_detail_id = planned_detail_id
        self.detail_id = detail_id
        self.required_quantity = required_quantity
        self.in_stock_quantity = in_stock_quantity
        super().__init__(self.message)

    def __str__(self):
        return (
            f"{self.message}: "
            f"Planned Detail ID - {self.detail_id} "
            f"Detailed ID - {self.detail_id},"
            f"required - {self.required_quantity}, "
            f"in stock - {self.in_stock_quantity}"
        )


class AllocationDetailError(Exception):

    def __init__(self, message: str, planned_detail_id: int, task_id: int | None = None):
        self.message = message
        self.planned_detail_id = planned_detail_id
        self.task_id = task_id

        super().__init__(self.message)

    def __str__(self):
        msg = f"{self.message}: {self.planned_detail_id}"
        if self.task_id:
            msg += f" - {self.task_id}"
        return msg
