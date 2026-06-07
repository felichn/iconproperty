from django.contrib import admin

from .models import Property, PropertyPhoto


class PropertyPhotoInline(admin.TabularInline):
    model = PropertyPhoto
    extra = 1


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = (
        "unit",
        "property_type",
        "listing_mode",
        "block",
        "unit_no",
        "price",
        "area",
        "floors",
        "owner_whatsapp_number",
    )
    list_filter = ("property_type", "listing_mode", "floors", "area", "block")
    search_fields = ("title", "area", "owner_whatsapp_number", "block", "=unit_no")
    inlines = [PropertyPhotoInline]


@admin.register(PropertyPhoto)
class PropertyPhotoAdmin(admin.ModelAdmin):
    list_display = ("id", "property", "uploaded_at")
    search_fields = ("property__title",)

# Register your models here.
