from django.db import models


class Detail(models.Model):
    name = models.CharField(max_length=255)
    unit_of_measurement = models.CharField(max_length=10)
    price_for_unit = models.DecimalField(max_digits=10, decimal_places=2)
    similar_details = models.ManyToManyField(
        'self',
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"{self.id} - {self.name}"

    class Meta:
        verbose_name = 'Detail'
        verbose_name_plural = 'Details'


class PlannedDetail(models.Model):
    detail = models.ForeignKey(Detail, on_delete=models.CASCADE)
    task = models.ForeignKey('tasks.Task', on_delete=models.CASCADE, related_name='planned_details')
    planned_quantity = models.PositiveIntegerField(default=0)
    quantity_in_stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"id: {self.id} - detail: {self.detail}"

    class Meta:
        verbose_name = 'Planned Detail'
        verbose_name_plural = 'Planned Details'
        ordering = ['id']


class DetailInStock(models.Model):
    detail = models.ForeignKey(Detail, on_delete=models.CASCADE, related_name='details_in_stock')
    quantity = models.PositiveIntegerField(default=0)
    warehouse = models.ForeignKey(
        'WareHouse',
        on_delete=models.CASCADE,
        related_name='details_in_stock',
    )

    def __str__(self):
        return f"id: {self.id} - detail: {self.detail} - pcs: {self.quantity}"

    class Meta:
        verbose_name = 'Detail In Stock'
        verbose_name_plural = 'Details In Stock'
        ordering = ['id']


class WareHouse(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=255, unique=True)
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.id} - {self.name}"

    class Meta:
        verbose_name = 'Warehouse'
        verbose_name_plural = 'Warehouses'
        ordering = ['id']
