from django.contrib.auth.models import User
from rest_framework import serializers
from tasks.models import Task


class BaseTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = ['author', 'created_at', 'updated_at', 'id']


class CreateTaskSerializer(BaseTaskSerializer):
    executor = serializers.PrimaryKeyRelatedField(queryset=User.objects)


class SingleTaskSerializer(BaseTaskSerializer):
    from details.serializers import BasePlannedDetailSerializer
    planned_details = BasePlannedDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = BaseTaskSerializer.Meta.fields
        read_only_fields = ['author', 'created_at', 'updated_at', 'id', 'planned_details']


class ListTaskSerializer(SingleTaskSerializer):
    pass
