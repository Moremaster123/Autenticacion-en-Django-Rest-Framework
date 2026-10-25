from django.contrib import admin

from .models import Cart


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total', 'updated_at')
    search_fields = ('user__username',)
    filter_horizontal = ('products',)

    @admin.display(description='Total')
    def total(self, obj):
        return obj.get_total()
