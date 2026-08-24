from rest_framework import generics
from rest_framework.permissions import AllowAny

from .models import Building, City, Locality
from .serializers import BuildingSerializer, CitySerializer, LocalitySerializer


class CityListView(generics.ListAPIView):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    permission_classes = [AllowAny]
    pagination_class = None


class LocalityListView(generics.ListAPIView):
    serializer_class = LocalitySerializer
    permission_classes = [AllowAny]
    pagination_class = None

    def get_queryset(self):
        qs = Locality.objects.select_related("city")
        city = self.request.query_params.get("city")
        return qs.filter(city_id=city) if city else qs


class BuildingListView(generics.ListAPIView):
    serializer_class = BuildingSerializer
    permission_classes = [AllowAny]
    pagination_class = None

    def get_queryset(self):
        qs = Building.objects.select_related("locality")
        locality = self.request.query_params.get("locality")
        return qs.filter(locality_id=locality) if locality else qs
