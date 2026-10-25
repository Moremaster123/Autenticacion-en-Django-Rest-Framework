from django.contrib import admin

from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'billing_profile', 'status', 'total', 'updated_at')
    list_filter = ('status', 'created_at')
    search_fields = ('billing_profile__email',)
    readonly_fields = ('created_at', 'updated_at')
