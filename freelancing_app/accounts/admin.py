from django.contrib import admin
from .models import Country, City

@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    """
    Custom admin interface for Country model with:
    - Basic list display
    - Search functionality
    """
    list_display = ('id', 'name', 'code')
    search_fields = ('name', 'code')
    ordering = ('name',)
    fields = ('name', 'code')

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    """
    Custom admin interface for City model with:
    - Related country display
    - Enhanced filtering
    - Optimized queries
    """
    list_display = ('id', 'name', 'country')
    search_fields = ('name', 'country__name')
    list_filter = ('country',)
    ordering = ('name',)
    raw_id_fields = ('country',)  # Better for large country lists
    autocomplete_fields = ['country']  # Requires search_fields in CountryAdmin
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('country')