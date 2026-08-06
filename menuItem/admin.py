from django.contrib import admin
# pyrefly: ignore [missing-import]
from .models import MenuItem
# Register your models here.
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "category", "price", "menu", "created_at", "updated_at")
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("id", "name", "category", "price", "menu", "created_at", "updated_at"),
        }),
    )
    edit_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("id", "name", "category", "price", "menu", "created_at", "updated_at"),
        }),
    )
    search_fields = ("name", "category")
    list_filter = ("created_at", "updated_at")
    ordering = ("-created_at",)
    

admin.site.register(MenuItem,MenuItemAdmin)    
