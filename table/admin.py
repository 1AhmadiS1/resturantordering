
from django.contrib import admin

from .models import Table

# Register your models here.
@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "restaurant",
        "table_number",
        "capacity",
        "status",
        "created_at",
        "updated_at",
    )
    list_filter = ("status",)
    search_fields = ("table_number", "restaurant__name")
    ordering = ("-created_at",)
    fieldsets = (
        (
            "Table Information",
            {"fields": ("restaurant", "table_number", "capacity", "status")},
        ),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )
    readonly_fields = ("created_at", "updated_at")

