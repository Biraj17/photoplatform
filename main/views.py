from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from accounts.models import Photographer

from .models import Offer


def home(request):
    return render(request, "main/home.html")


def about(request):
    return render(request, "main/home.html")


def profile_photographer(request, pk=None):
    if pk is None:
        photographer = get_object_or_404(
            Photographer.objects.select_related("user").prefetch_related("portfolio_images", "projects").order_by("-created_at")[:1]
        )
    else:
        photographer = get_object_or_404(
            Photographer.objects.select_related("user").prefetch_related("portfolio_images", "projects"),
            pk=pk,
        )
    return render(request, "main/photographer_profile.html", {
        "photographer": photographer,
        "portfolio_images": photographer.portfolio_images.all(),
        "projects": photographer.projects.all(),
    })


def photographers_list(request):
    photographers = Photographer.objects.select_related("user").all()
    return render(request, "main/photographers.html", {
        "photographers": photographers,
    })


def offers_list(request):
    today = timezone.localdate()
    offers = Offer.objects.filter(is_active=True, ends_at__gte=today)
    return render(request, "main/offers.html", {
        "offers": offers,
    })
