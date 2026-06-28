from django.contrib import admin

from .models import Offer


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ("title", "discount_percent", "ends_at", "is_active", "created_at")
    list_filter = ("is_active", "ends_at")
    search_fields = ("title", "description")
    date_hierarchy = "ends_at"
