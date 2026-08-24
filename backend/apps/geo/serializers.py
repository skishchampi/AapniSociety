from rest_framework import serializers

from .models import Building, City, Locality, Unit


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ["id", "name", "state", "slug"]


class LocalitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Locality
        fields = ["id", "city", "name", "slug"]


class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = ["id", "building", "label"]


class BuildingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Building
        fields = ["id", "locality", "name", "address", "lat", "lng"]
