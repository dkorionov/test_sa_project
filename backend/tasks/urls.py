from django.urls import path
from tasks.views import (
    CreateListTaskView, RetrieveUpdateDestroyTaskView,
    UpdateCompletedTaskView, UpdateInProgressTaskView,
    UpdateReviewTaskView,
)

urlpatterns = [
    path('', CreateListTaskView.as_view(), name='list-create-task'),
    path('<int:pk>/', RetrieveUpdateDestroyTaskView.as_view(), name='retrieve-update-delete-task'),

    path('update-in-progress/<int:pk>/', UpdateInProgressTaskView.as_view(), name='update-to-in-progress'),
    path('update-review/<int:pk>/', UpdateReviewTaskView.as_view(), name='update-to-review'),
    path('update-completed/<int:pk>/', UpdateCompletedTaskView.as_view(), name='update-to-completed'),
]
