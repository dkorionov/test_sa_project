from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from sa_project.services.base_permission import IsAuthorOrExecutorReadOnly
from sa_project.services.base_view import BaseAPIView
from tasks.serializers import (
    BaseTaskSerializer, CreateTaskSerializer,
    ListTaskSerializer, SingleTaskSerializer,
)
from tasks.services import TaskDAO


class BaseTaskView(BaseAPIView):
    serializer_class = SingleTaskSerializer
    controller: TaskDAO = TaskDAO
    queryset = controller.model.objects.all()
    permission_classes = [IsAuthenticated, IsAuthorOrExecutorReadOnly]


class CreateListTaskView(generics.ListCreateAPIView, BaseTaskView):
    serializer_class = ListTaskSerializer

    @extend_schema(responses=CreateTaskSerializer, request=CreateTaskSerializer)
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer: CreateTaskSerializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        controller = self.get_controller()
        q = controller.get_all_task_with_planned_details(user=self.request.user)
        return self.filter_queryset(q)


class RetrieveUpdateDestroyTaskView(BaseTaskView, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BaseTaskSerializer

    @extend_schema(responses=SingleTaskSerializer)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class UpdateTaskView(BaseTaskView, generics.UpdateAPIView):
    serializer_class = BaseTaskSerializer


class UpdateInProgressTaskView(BaseTaskView):

    @extend_schema(
        responses=BaseTaskSerializer,
        request=None,
    )
    def patch(self, request, *args, **kwargs):
        obj = self.get_object()
        controller = self.get_controller()
        controller.change_to_in_progress(obj)
        return Response(data=self.serializer_class(obj).data, status=200)


class UpdateReviewTaskView(BaseTaskView):

    @extend_schema(responses=BaseTaskSerializer, request=None)
    def patch(self, request, *args, **kwargs):
        obj = self.get_object()
        controller = self.get_controller()
        controller.change_to_review(obj)
        return Response(data=self.serializer_class(obj).data, status=200)


class UpdateCompletedTaskView(BaseTaskView):

    @extend_schema(responses=BaseTaskSerializer, request=None)
    def patch(self, serializer: CreateTaskSerializer):
        obj = self.get_object()
        controller = self.get_controller()
        controller.change_to_completed(obj)
        return Response(data=self.serializer_class(obj).data, status=200)
