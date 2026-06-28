from django.shortcuts import render
from django.utils import timezone

from accounts.models import Photographer

from .models import Offer


def home(request):
    return render(request, "main/home.html")


def about(request):
    return render(request, "main/home.html")


def profile_photographer(request):
    return render(request, "main/photographer_profile.html")


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
