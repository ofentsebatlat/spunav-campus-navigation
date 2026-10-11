from django.contrib import admin
from .models import Location, Path, RouteHistory

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'building_code', 'location_type', 'latitude', 'longitude')
    search_fields = ('name', 'building_code', 'location_type')
    list_filter = ('location_type',)

@admin.register(Path)
class PathAdmin(admin.ModelAdmin):
    list_display = ('start_location', 'end_location', 'distance', 'crowd_level', 'get_total_weight')
    search_fields = ('start_location__name', 'end_location__name')
    list_filter = ('crowd_level',)

    def get_total_weight(self, obj):
        return obj.get_weight()
    get_total_weight.short_description = 'Total Weight (Dist x Crowd)'

@admin.register(RouteHistory)
class RouteHistoryAdmin(admin.ModelAdmin):
    list_display = ('start', 'destination', 'user', 'timestamp', 'distance', 'travel_time')
    list_filter = ('timestamp', 'user')
