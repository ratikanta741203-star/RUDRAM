from django.contrib import admin
from apps.shelters.models import Shelter

@admin.register(Shelter)
class ShelterAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'current_occupancy', 'total_capacity', 'occupancy_percentage', 'has_medical_station', 'elevation_m', 'phone_number')
    list_filter = ('status', 'has_medical_station', 'has_potable_water', 'has_food_stocks')
    search_fields = ('name', 'address', 'contact_person')
