from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html

from .models import Photographer, PhotographerProject, PortfolioImage, SavedPhotographer

KYC_REVIEWER_GROUP = "KYC Reviewers"

PROFILE_FIELDS = (
    "user",
    "full_name",
    "city",
    "address",
    "phone",
    "contact_email",
    "bio",
    "specialty",
    "years_experience",
    "price_per_shoot",
    "rating",
    "profile_image",
)


@admin.register(Photographer)
class PhotographerAdmin(admin.ModelAdmin):
    list_display = ("full_name", "city", "specialty", "price_per_shoot", "rating", "kyc_status", "kyc_submitted_at", "user", "created_at")
    search_fields = ("full_name", "user__email", "contact_email", "phone", "city", "citizenship_number")
    list_filter = ("specialty", "city", "kyc_status")
    readonly_fields = ("created_at", "kyc_submitted_at", "kyc_reviewed_at", "citizenship_front_preview", "citizenship_back_preview")
    actions = ("mark_kyc_verified", "mark_kyc_rejected", "mark_kyc_pending")
    fieldsets = (
        ("Profile", {"fields": PROFILE_FIELDS}),
        ("KYC verification", {
            "fields": (
                "citizenship_number",
                "citizenship_front", "citizenship_front_preview",
                "citizenship_back", "citizenship_back_preview",
                "kyc_status", "kyc_submitted_at", "kyc_reviewed_at",
            ),
        }),
        ("Meta", {"fields": ("created_at",)}),
    )

    def citizenship_front_preview(self, obj):
        return self._doc_preview(obj.citizenship_front)
    citizenship_front_preview.short_description = "Front photo preview"

    def citizenship_back_preview(self, obj):
        return self._doc_preview(obj.citizenship_back)
    citizenship_back_preview.short_description = "Back photo preview"

    def _doc_preview(self, file_field):
        if not file_field:
            return "No document uploaded."
        return format_html('<img src="{}" style="max-height:220px;border:1px solid #ccc;" />', file_field.url)

    def get_readonly_fields(self, request, obj=None):
        readonly = list(self.readonly_fields)
        if not request.user.is_superuser and request.user.groups.filter(name=KYC_REVIEWER_GROUP).exists():
            readonly = [f for f in (PROFILE_FIELDS + ("citizenship_number", "citizenship_front", "citizenship_back"))] + readonly
        return readonly

    def save_model(self, request, obj, form, change):
        if change and "kyc_status" in form.changed_data:
            obj.kyc_reviewed_at = timezone.now()
        super().save_model(request, obj, form, change)

    def _mark_kyc(self, request, queryset, status):
        updated = queryset.update(kyc_status=status, kyc_reviewed_at=timezone.now())
        self.message_user(request, f"{updated} photographer(s) marked as {status}.")

    def mark_kyc_verified(self, request, queryset):
        self._mark_kyc(request, queryset, Photographer.KYC_VERIFIED)
    mark_kyc_verified.short_description = "Mark KYC as Verified"

    def mark_kyc_rejected(self, request, queryset):
        self._mark_kyc(request, queryset, Photographer.KYC_REJECTED)
    mark_kyc_rejected.short_description = "Mark KYC as Rejected"

    def mark_kyc_pending(self, request, queryset):
        self._mark_kyc(request, queryset, Photographer.KYC_PENDING)
    mark_kyc_pending.short_description = "Mark KYC as Pending"


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


@admin.register(SavedPhotographer)
class SavedPhotographerAdmin(admin.ModelAdmin):
    list_display = ("user", "photographer", "created_at")
    search_fields = ("user__email", "photographer__full_name")
    readonly_fields = ("created_at",)
