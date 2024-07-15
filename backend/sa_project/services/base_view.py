from typing import Type

from rest_framework.generics import GenericAPIView, get_object_or_404

from .base_dao import BaseDao


class BaseAPIView(GenericAPIView):
    controller: Type[BaseDao]

    def get_object(self, *args, **kwargs):
        obj = get_object_or_404(self.controller.model, pk=self.kwargs['pk'])
        self.check_object_permissions(self.request, obj)
        return obj

    def get_controller(self):
        return self.controller()
