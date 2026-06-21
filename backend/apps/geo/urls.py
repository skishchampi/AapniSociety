from django.urls import path

from .views import BuildingListView, CityListView, LocalityListView

urlpatterns = [
    path("cities/", CityListView.as_view(), name="cities"),
    path("localities/", LocalityListView.as_view(), name="localities"),
    path("buildings/", BuildingListView.as_view(), name="buildings"),
]
