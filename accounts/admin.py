from django.contrib import admin

from .models import Photographer, PhotographerProject, PortfolioImage


@admin.register(Photographer)
class PhotographerAdmin(admin.ModelAdmin):
    list_display = ("full_name", "city", "phone", "contact_email", "specialty", "price_per_shoot", "rating", "user", "created_at")
    search_fields = ("full_name", "user__email", "contact_email", "phone", "city")
    list_filter = ("specialty", "city")
    readonly_fields = ("created_at",)


@admin.register(PortfolioImage)
class PortfolioImageAdmin(admin.ModelAdmin):
    list_display = ("photographer", "caption", "created_at")
    search_fields = ("photographer__full_name", "caption")
    readonly_fields = ("created_at",)


@admin.register(PhotographerProject)
class PhotographerProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "photographer", "location", "completed_at", "created_at")
    search_fields = ("title", "photographer__full_name", "location")
    readonly_fields = ("created_at",)
