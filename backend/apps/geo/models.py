from django.db import models


class City(models.Model):
    name = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name_plural = "cities"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Locality(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name="localities")
    name = models.CharField(max_length=120)
    slug = models.SlugField()

    class Meta:
        verbose_name_plural = "localities"
        ordering = ["name"]
        unique_together = [("city", "slug")]

    def __str__(self):
        return f"{self.name}, {self.city.name}"


class Building(models.Model):
    locality = models.ForeignKey(
        Locality, on_delete=models.CASCADE, related_name="buildings"
    )
    name = models.CharField(max_length=150)
    address = models.TextField(blank=True)
    # PostGIS-ready: nullable decimals now; swap to PointField when geo lands (0.3.0).
    lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.locality.name})"


class Unit(models.Model):
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name="units")
    label = models.CharField(max_length=50)

    class Meta:
        ordering = ["label"]
        unique_together = [("building", "label")]

    def __str__(self):
        return f"{self.building.name} / {self.label}"
