from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.functions.datetime import timezone


def validate_future_date(value):
    if value <= timezone.now().date():
        raise ValidationError('The date must be in the future.')


class Task(models.Model):
    class Status(models.TextChoices):
        TODO = 'To do', 'To Do'
        IN_PROGRESS = 'In Progress', 'In Progress'
        REVIEW = 'Review', 'Review'
        COMPLETED = 'Completed', 'Completed'

    description = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.TODO)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    expected_date = models.DateField(validators=[validate_future_date])
    author = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='created_tasks')
    executor = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='tasks_to_do')

    def __str__(self):
        return f"id: {self.id} - author: {self.author} - executor: {self.executor}"

    class Meta:
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'
        ordering = ['id']
