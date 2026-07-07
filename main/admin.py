from django.contrib import admin

from .models import BookingRequest, Offer


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ("title", "photographer", "discount_percent", "ends_at", "is_active", "created_at")
    list_filter = ("is_active", "ends_at")
    search_fields = ("title", "description", "photographer__full_name")
    date_hierarchy = "ends_at"


@admin.register(BookingRequest)
class BookingRequestAdmin(admin.ModelAdmin):
    list_display = ("client_name", "photographer", "shoot_date", "package", "is_read", "created_at")
    list_filter = ("package", "is_read", "shoot_date")
    search_fields = ("client_name", "client_email", "client_phone", "photographer__full_name")
    readonly_fields = ("created_at",)
