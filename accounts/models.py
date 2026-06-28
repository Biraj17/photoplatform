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

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="photographer_profile",
    )
    full_name = models.CharField(max_length=150)
    city = models.CharField(max_length=100, blank=True, default="Nepal")
    specialty = models.CharField(max_length=20, choices=SPECIALTY_CHOICES, default="Portrait")
    years_experience = models.PositiveSmallIntegerField(default=1)
    price_per_shoot = models.PositiveIntegerField(default=0, help_text="Price in Nepalese Rupees")
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=5.0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.full_name
