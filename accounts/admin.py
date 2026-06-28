from django.contrib import admin

from .models import Photographer


@admin.register(Photographer)
class PhotographerAdmin(admin.ModelAdmin):
    list_display = ("full_name", "city", "specialty", "price_per_shoot", "rating", "user", "created_at")
    search_fields = ("full_name", "user__email", "city")
    list_filter = ("specialty", "city")
    readonly_fields = ("created_at",)
