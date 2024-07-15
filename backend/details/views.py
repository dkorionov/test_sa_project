from details.serializers import (
    BaseDetailSerializer,
    BasePlannedDetailSerializer,
    CreateDetailSerializer,
    CreatePlannedDetailsSerializer,
    DetailInStockSerializer,
    DetailWithSimilarDetailsSerializer,
)
from details.services import DetailDAO, DetailInStockDAO, PlannedDetailDAO
from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from sa_project.services.base_view import BaseAPIView


class BaseDetailView(BaseAPIView):
    serializer_class = BaseDetailSerializer
    controller = DetailDAO
    permission_classes = [IsAuthenticated]
    queryset = DetailDAO.model.objects.all()


class BasePlannedDetailsView(BaseAPIView):
    serializer_class = BasePlannedDetailSerializer
    controller = PlannedDetailDAO
    permission_classes = [IsAuthenticated]
    queryset = PlannedDetailDAO.model.objects.all()


class BaseDetailInStockView(BaseAPIView):
    serializer_class = DetailInStockSerializer
    controller = DetailInStockDAO
    permission_classes = [IsAuthenticated]
    queryset = DetailInStockDAO.model.objects.all()


class ListCreateDetail(generics.ListCreateAPIView, BaseDetailView):

    @extend_schema(responses=CreateDetailSerializer, request=CreateDetailSerializer)
    def post(self, request, *args, **kwargs):
        self.serializer_class = CreateDetailSerializer
        return super().post(request, *args, **kwargs)

    @extend_schema(responses=DetailWithSimilarDetailsSerializer)
    def get(self, request, *args, **kwargs):
        self.serializer_class = DetailWithSimilarDetailsSerializer
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        controller = self.get_controller()
        q = controller.get_all_details_with_similar_details()
        return self.filter_queryset(q)


class RetrieveUpdateDestroyDetailView(generics.RetrieveUpdateDestroyAPIView, BaseDetailView):
    pass


class ListCreatePlannedDetails(generics.ListCreateAPIView, BasePlannedDetailsView):

    @extend_schema(responses=CreatePlannedDetailsSerializer, request=CreatePlannedDetailsSerializer)
    def post(self, request, *args, **kwargs):
        self.serializer_class = CreatePlannedDetailsSerializer
        return super().post(request, *args, **kwargs)


class RetrieveUpdateDestroyPlannedDetails(generics.RetrieveUpdateDestroyAPIView, BasePlannedDetailsView):
    pass
