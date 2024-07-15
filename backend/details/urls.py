from details.views import (
    ListCreateDetail, ListCreatePlannedDetails,
    RetrieveUpdateDestroyDetailView,
    RetrieveUpdateDestroyPlannedDetails,
)
from django.urls import include, path

urlpatterns = [
    path('', ListCreateDetail.as_view(), name='list-create-detail'),
    path('<int:pk>/', RetrieveUpdateDestroyDetailView.as_view(), name='retrieve-update-destroy-detail'),
    path(
        'planned-details/', include([
            path('', ListCreatePlannedDetails.as_view(), name='list-create-planned-detail'),
            path('<int:pk>/', RetrieveUpdateDestroyPlannedDetails.as_view(), name='retrieve-update-destroy-planned-detail'),

        ]),
    ),

]
