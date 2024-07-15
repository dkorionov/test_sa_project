from typing import Dict, Type, TypeVar

from django.db.models import Model, QuerySet

T = TypeVar('T', bound=Model)


class BaseDao:
    model: Type[T]

    def get(self, obj_id: int) -> T:
        return self.model.objects.get(id=obj_id)

    def get_all(self) -> QuerySet[T]:
        return self.model.objects.all()

    def create(self, data: Dict) -> T:
        return self.model.objects.create(**data)

    def update(self, obj: T, data: Dict) -> T:
        for key, value in data.items():
            setattr(obj, key, value)
        obj.save(update_fields=data.keys())
        return obj

    def delete(self, obj: T):
        obj.delete()
