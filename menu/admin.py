from django.contrib import admin
from .models import Menu
# Register your models here.
class MenuAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "description", "restuarant", "created_at", "updated_at")
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("id", "name", "description", "restuarant", "created_at", "updated_at"),
        }),
    )
    edit_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("id", "name", "description", "restuarant", "created_at", "updated_at"),
        }),
    )
    search_fields = ("name", "description")
    list_filter = ("created_at", "updated_at")
    ordering = ("-created_at",)
    

admin.site.register(Menu,MenuAdmin)
