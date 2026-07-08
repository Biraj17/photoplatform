from django.conf import settings
from django.db import models


class Photographer(models.Model):
    SPECIALTY_CHOICES = [
        ("Wedding", "Wedding"),
        ("Portrait", "Portrait"),
        ("Family", "Family"),
        ("Fashion", "Fashion"),
        ("Travel", "Travel"),
    ]

    KYC_PENDING = "Pending"
    KYC_VERIFIED = "Verified"
    KYC_REJECTED = "Rejected"
    KYC_STATUS_CHOICES = [
        (KYC_PENDING, "Pending"),
        (KYC_VERIFIED, "Verified"),
        (KYC_REJECTED, "Rejected"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="photographer_profile",
    )
    full_name = models.CharField(max_length=150)
    city = models.CharField(max_length=100, blank=True, default="Nepal")
    address = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    contact_email = models.EmailField(blank=True)
    bio = models.TextField(blank=True)
    specialty = models.CharField(max_length=20, choices=SPECIALTY_CHOICES, default="Portrait")
    years_experience = models.PositiveSmallIntegerField(default=1)
    price_per_shoot = models.PositiveIntegerField(default=0, help_text="Price in Nepalese Rupees")
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=5.0)
    profile_image = models.FileField(upload_to="photographers/profiles/", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    citizenship_number = models.CharField(max_length=40)
    citizenship_front = models.FileField(upload_to="photographers/kyc/", blank=True)
    citizenship_back = models.FileField(upload_to="photographers/kyc/", blank=True)
    kyc_status = models.CharField(max_length=10, choices=KYC_STATUS_CHOICES, default=KYC_PENDING)
    kyc_submitted_at = models.DateTimeField(blank=True, null=True)
    kyc_reviewed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.full_name

    @property
    def is_kyc_verified(self):
        return self.kyc_status == self.KYC_VERIFIED

    @property
    def has_submitted_kyc(self):
        return bool(self.citizenship_number and self.citizenship_front and self.citizenship_back)


class PortfolioImage(models.Model):
    photographer = models.ForeignKey(
        Photographer,
        on_delete=models.CASCADE,
        related_name="portfolio_images",
    )
    image = models.FileField(upload_to="photographers/portfolio/")
    caption = models.CharField(max_length=150, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.caption or f"Portfolio image for {self.photographer.full_name}"


class PhotographerProject(models.Model):
    photographer = models.ForeignKey(
        Photographer,
        on_delete=models.CASCADE,
        related_name="projects",
    )
    title = models.CharField(max_length=150)
    location = models.CharField(max_length=120, blank=True)
    completed_at = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True)
    cover_image = models.FileField(upload_to="photographers/projects/", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-completed_at", "-created_at"]

    def __str__(self):
        return self.title


class SavedPhotographer(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="saved_photographers",
    )
    photographer = models.ForeignKey(
        Photographer,
        on_delete=models.CASCADE,
        related_name="saved_by",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "photographer")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} saved {self.photographer}"
