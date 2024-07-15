from details.models import Detail, DetailInStock, PlannedDetail
from rest_framework import serializers
from tasks.models import Task


class BaseDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Detail
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'id']


class CreateDetailSerializer(BaseDetailSerializer):
    similar_details = serializers.PrimaryKeyRelatedField(many=True, queryset=Detail.objects)


class DetailWithSimilarDetailsSerializer(BaseDetailSerializer):
    similar_details = BaseDetailSerializer(many=True, read_only=True)


class BasePlannedDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlannedDetail
        fields = '__all__'
        read_only_fields = ['id', 'quantity_in_stock']


class CreatePlannedDetailsSerializer(BasePlannedDetailSerializer):
    detail = serializers.PrimaryKeyRelatedField(queryset=Detail.objects)
    task = serializers.PrimaryKeyRelatedField(queryset=Task.objects)


class DetailInStockSerializer(serializers.ModelSerializer):
    detail = BaseDetailSerializer(read_only=True)

    class Meta:
        model = DetailInStock
        fields = '__all__'
        read_only_fields = ['id']
