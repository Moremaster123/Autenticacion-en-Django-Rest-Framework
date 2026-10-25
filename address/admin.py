from django.contrib import admin

from .models import Address


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('street', 'city', 'state', 'country', 'postal_code')
    list_filter = ('country', 'state')
    search_fields = ('street', 'city', 'postal_code')
