from django.db import models
from django.contrib.auth.models import User

class Location(models.Model):
    LOCATION_TYPES = [
        ('LECTURE_HALL', 'Lecture Hall'),
        ('LAB', 'Computer Lab'),
        ('LIBRARY', 'Library'),
        ('CAFETERIA', 'Cafeteria'),
        ('ADMIN', 'Admin Office'),
        ('RESIDENCE', 'Residence'),
        ('OTHER', 'Other'),
    ]

    name = models.CharField(max_length=200)
    building_code = models.CharField(max_length=50, blank=True, null=True)
    location_type = models.CharField(max_length=20, choices=LOCATION_TYPES, default='OTHER')
    latitude = models.FloatField(help_text="For visualization purposes", default=0.0)
    longitude = models.FloatField(help_text="For visualization purposes", default=0.0)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.get_location_type_display()})"

class Path(models.Model):
    start_location = models.ForeignKey(Location, related_name='paths_from', on_delete=models.CASCADE)
    end_location = models.ForeignKey(Location, related_name='paths_to', on_delete=models.CASCADE)
    distance = models.FloatField(help_text="Distance in meters")
    crowd_level = models.FloatField(default=1.0, help_text="Crowd factor (1.0 = no crowd, >1.0 = crowded)")

    def get_weight(self):
        """Dynamic weight calculation: Weight = Distance × Crowd Factor"""
        return self.distance * self.crowd_level

    def __str__(self):
        return f"{self.start_location.name} to {self.end_location.name} (Dist: {self.distance}, Crowd: {self.crowd_level})"

class RouteHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    start = models.ForeignKey(Location, related_name='history_starts', on_delete=models.CASCADE)
    destination = models.ForeignKey(Location, related_name='history_destinations', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    distance = models.FloatField(null=True, blank=True)
    travel_time = models.FloatField(null=True, blank=True, help_text="Estimated travel time in minutes")

    class Meta:
        verbose_name_plural = "Route Histories"

    def __str__(self):
        return f"{self.start.name} -> {self.destination.name} at {self.timestamp}"
