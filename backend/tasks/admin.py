from django.contrib import admin
from tasks.models import Task


class TaskAdmin(admin.ModelAdmin):
    list_filter = ['status', 'author', 'executor']
    search_fields = ['title']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['id', 'expected_date']


admin.site.register(Task, TaskAdmin)
