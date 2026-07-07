from django.db import models
from django.utils import timezone

from accounts.models import Photographer


class Offer(models.Model):
    title = models.CharField(max_length=120)
    discount_percent = models.PositiveSmallIntegerField(help_text="Discount percentage, e.g. 20 for 20% off")
    description = models.TextField(max_length=300)
    ends_at = models.DateField(help_text="Last day this offer is valid")
    icon = models.CharField(max_length=40, default="fa-tag", help_text="Font Awesome 4 icon class")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["ends_at"]

    def __str__(self):
        return self.title

    @property
    def is_current(self):
        return self.is_active and self.ends_at >= timezone.localdate()

    @property
    def duration_label(self):
        today = timezone.localdate()
        if self.ends_at < today:
            return "Expired"
        days_left = (self.ends_at - today).days
        if days_left == 0:
            return "Ends today"
        if days_left == 1:
            return "Ends tomorrow"
        if days_left <= 7:
            return f"Ends in {days_left} days"
        if days_left <= 31:
            return "This month"
        return f"Until {self.ends_at.strftime('%b %d, %Y')}"


class BookingRequest(models.Model):
    PACKAGE_CHOICES = [
        ("Essential", "Essential"),
        ("Signature", "Signature"),
        ("Full Day", "Full Day"),
        ("Custom", "Custom"),
    ]

    photographer = models.ForeignKey(
        Photographer,
        on_delete=models.CASCADE,
        related_name="booking_requests",
    )
    client_name = models.CharField(max_length=120)
    client_email = models.EmailField()
    client_phone = models.CharField(max_length=30)
    shoot_date = models.DateField(blank=True, null=True)
    package = models.CharField(max_length=20, choices=PACKAGE_CHOICES, default="Custom")
    message = models.TextField(blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.client_name} -> {self.photographer.full_name}"
