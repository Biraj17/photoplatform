from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.models import Photographer, SavedPhotographer

from .forms import BookingRequestForm, PhotographerSearchForm
from .models import Offer


def home(request):
    today = timezone.localdate()
    photographers = Photographer.objects.select_related("user").order_by("-rating", "-created_at")[:4]
    offers = Offer.objects.filter(is_active=True, ends_at__gte=today)[:3]
    return render(request, "main/home.html", {
        "search_form": PhotographerSearchForm(),
        "photographers": photographers,
        "offers": offers,
    })


def about(request):
    return info_page(request, "about")


def profile_photographer(request, pk=None):
    if pk is None:
        photographer = Photographer.objects.select_related("user").prefetch_related("portfolio_images", "projects").order_by("-created_at").first()
        if photographer is None:
            raise Http404("No photographer profiles are available yet.")
    else:
        photographer = get_object_or_404(
            Photographer.objects.select_related("user").prefetch_related("portfolio_images", "projects"),
            pk=pk,
        )
    today = timezone.localdate()
    photographer_offers = photographer.offers.filter(is_active=True, ends_at__gte=today)
    booking_form = BookingRequestForm(request.POST or None)
    if request.method == "POST" and request.POST.get("action") == "book":
        if booking_form.is_valid():
            booking_request = booking_form.save(commit=False)
            booking_request.photographer = photographer
            booking_request.save()
            messages.success(request, "Your booking request was sent. The photographer can now see it in their dashboard.")
            return redirect("photographer_profile_detail", pk=photographer.pk)

    is_saved = False
    if request.user.is_authenticated:
        is_saved = SavedPhotographer.objects.filter(user=request.user, photographer=photographer).exists()

    return render(request, "main/photographer_profile.html", {
        "photographer": photographer,
        "portfolio_images": photographer.portfolio_images.all(),
        "projects": photographer.projects.all(),
        "photographer_offers": photographer_offers,
        "booking_form": booking_form,
        "is_saved": is_saved,
    })


def photographers_list(request):
    photographers = Photographer.objects.select_related("user").all()
    specialty = request.GET.get("specialty", "").strip()
    location = request.GET.get("location", "").strip()
    query = request.GET.get("q", "").strip()

    if specialty:
        photographers = photographers.filter(specialty=specialty)
    if location:
        photographers = photographers.filter(city__icontains=location)
    if query:
        photographers = photographers.filter(full_name__icontains=query)

    return render(request, "main/photographers.html", {
        "photographers": photographers,
        "active_specialty": specialty,
        "active_location": location,
        "query": query,
        "specialties": Photographer.SPECIALTY_CHOICES,
    })


def offers_list(request):
    today = timezone.localdate()
    offers = Offer.objects.filter(is_active=True, ends_at__gte=today)
    return render(request, "main/offers.html", {
        "offers": offers,
    })


@login_required(login_url="photographer_login")
def toggle_saved_photographer(request, pk):
    photographer = get_object_or_404(Photographer, pk=pk)
    saved, created = SavedPhotographer.objects.get_or_create(user=request.user, photographer=photographer)
    if created:
        messages.success(request, f"{photographer.full_name} was added to your saved list.")
    else:
        saved.delete()
        messages.info(request, f"{photographer.full_name} was removed from your saved list.")
    next_url = request.POST.get("next") or request.GET.get("next") or "photographers_list"
    return redirect(next_url)


INFO_PAGES = {
    "about": {
        "eyebrow": "Company",
        "title": "About PhotoPlat",
        "body": "PhotoPlat helps people in Nepal find photographers by style, location, budget, and real portfolio work. Photographers can manage their public profile, upload work, and receive booking requests.",
    },
    "how-it-works": {
        "eyebrow": "Guide",
        "title": "How it works",
        "body": "Search by category and location, compare profiles, save photographers you like, and send a booking request from the profile page. Photographers receive requests in their dashboard.",
    },
    "careers": {
        "eyebrow": "Company",
        "title": "Careers",
        "body": "PhotoPlat is a growing project. For now, the best way to get involved is to join as a photographer and help shape the marketplace.",
    },
    "press": {
        "eyebrow": "Company",
        "title": "Press",
        "body": "PhotoPlat is building a more direct way to discover and book photographers across Nepal.",
    },
    "help": {
        "eyebrow": "Support",
        "title": "Help center",
        "body": "Clients can search, view profiles, and send booking requests. Photographers can log in to edit profile details, upload images, add projects, and review incoming inquiries.",
    },
    "trust": {
        "eyebrow": "Support",
        "title": "Trust and safety",
        "body": "Use complete profiles, direct contact details, and project history to compare photographers before booking. Keep all important booking details written in the request message.",
    },
    "cancellation": {
        "eyebrow": "Support",
        "title": "Cancellation policy",
        "body": "Cancellation terms should be agreed directly between the client and photographer before the shoot date.",
    },
    "contact": {
        "eyebrow": "Support",
        "title": "Contact us",
        "body": "For platform questions, use the photographer profile contact details or reach the project owner through the social links in the footer.",
    },
    "privacy": {
        "eyebrow": "Legal",
        "title": "Privacy Policy",
        "body": "PhotoPlat stores account, profile, uploaded portfolio, project, saved photographer, and booking request information so the marketplace can function.",
    },
    "terms": {
        "eyebrow": "Legal",
        "title": "Terms of Service",
        "body": "By using PhotoPlat, photographers agree to keep profile information accurate and clients agree to send genuine booking requests.",
    },
    "sitemap": {
        "eyebrow": "Navigation",
        "title": "Sitemap",
        "body": "Use the navigation to visit Home, Photographers, Offers, Photographer Login, Join PhotoPlat, and support pages.",
    },
}


def info_page(request, slug):
    page = INFO_PAGES.get(slug)
    if page is None:
        raise Http404("Page not found")
    return render(request, "main/info_page.html", {
        "page": page,
        "slug": slug,
    })
