from django.contrib import admin

from .models import BillingProfile


@admin.register(BillingProfile)
class BillingProfileAdmin(admin.ModelAdmin):
    list_display = ('email', 'user', 'address', 'active', 'created_at')
    list_filter = ('active',)
    search_fields = ('email', 'user__username')
