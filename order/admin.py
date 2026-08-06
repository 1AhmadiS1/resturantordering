from .models import Order,OrderItem
from django.contrib import admin


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('menu_item')

class OrderAdmin(admin.ModelAdmin):
    list_display = ('restuarant', 'table', 'total_price', 'status', 'waiter', 'created_at')
    list_filter = ('restuarant', 'status', 'created_at', 'updated_at')
    search_fields = ('restuarant__name', 'table__table_number', 'waiter__email')
    readonly_fields = ('total_price', 'created_at', 'updated_at')
    inlines = [OrderItemInline]
    ordering = ('-created_at',)
    fieldsets = (
        (None, {
            "fields": (
                "restuarant",
                "table",
                "total_price",
                "status",
                "waiter",
                "note",
                "created_at",
                "updated_at",
            ),
        }),
    
    )
    

admin.site.register(Order, OrderAdmin)
