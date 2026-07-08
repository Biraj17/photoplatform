import os

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme

from main.forms import PhotographerOfferForm

from .forms import (
    PhotographerJoinForm,
    PhotographerKYCForm,
    PhotographerLoginForm,
    PhotographerProfileForm,
    PhotographerProjectForm,
    PortfolioImageForm,
)
from .models import Photographer


def register(request):
    return render(request, "accounts/register.html")


def bootstrap_admin(request):
    """One-time self-diagnosing setup endpoint. Permanently inert once any
    superuser exists — safe to leave deployed, but remove once confirmed."""
    if User.objects.filter(is_superuser=True).exists():
        return HttpResponse(
            "A superuser already exists. This endpoint is now inactive.\n"
            "Go to /admin/ to log in.",
            content_type="text/plain",
        )

    username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
    email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "")
    password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

    if not username or not password:
        return HttpResponse(
            "DJANGO_SUPERUSER_USERNAME and/or DJANGO_SUPERUSER_PASSWORD "
            "environment variables are not set on this service.",
            content_type="text/plain",
            status=400,
        )

    if User.objects.filter(username=username).exists():
        user = User.objects.get(username=username)
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.save()
        return HttpResponse(
            f"A user named '{username}' already existed (e.g. from signing up as a "
            f"photographer) — it has now been promoted to superuser with the password "
            f"from DJANGO_SUPERUSER_PASSWORD. Log in at /admin/.",
            content_type="text/plain",
        )

    User.objects.create_superuser(username=username, email=email, password=password)
    return HttpResponse(
        f"Superuser '{username}' created successfully. Log in at /admin/.",
        content_type="text/plain",
    )


def photographer_join(request):
    form = PhotographerJoinForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        photographer = form.save()
        login(request, photographer.user)
        messages.success(request, "Your account is ready. Add your contact details and work here.")
        return redirect("photographer_dashboard")

    return render(request, "accounts/photographer_join.html", {
        "form": form,
    })


def photographer_login(request):
    form = PhotographerLoginForm(request, data=request.POST or None)
    next_url = request.POST.get("next") or request.GET.get("next")

    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
            return redirect(next_url)
        return redirect("photographer_dashboard")

    return render(request, "accounts/login.html", {
        "form": form,
        "next": next_url,
    })


def photographer_logout(request):
    logout(request)
    return redirect("home")


@login_required(login_url="photographer_login")
def photographer_dashboard(request):
    try:
        photographer = request.user.photographer_profile
    except Photographer.DoesNotExist:
        messages.info(request, "Create a photographer profile before opening the dashboard.")
        return redirect("photographer_join_page")

    profile_form = PhotographerProfileForm(instance=photographer)
    kyc_form = PhotographerKYCForm(instance=photographer)
    image_form = PortfolioImageForm()
    project_form = PhotographerProjectForm()
    offer_form = PhotographerOfferForm()

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "save_profile":
            profile_form = PhotographerProfileForm(request.POST, request.FILES, instance=photographer)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, "Profile details updated.")
                return redirect("photographer_dashboard")
        elif action == "save_kyc":
            kyc_form = PhotographerKYCForm(request.POST, request.FILES, instance=photographer)
            if kyc_form.is_valid():
                submission = kyc_form.save(commit=False)
                submission.kyc_status = Photographer.KYC_PENDING
                submission.kyc_submitted_at = timezone.now()
                submission.kyc_reviewed_at = None
                submission.save()
                messages.success(request, "KYC documents submitted. Your verification is now pending review.")
                return redirect("photographer_dashboard")
        elif action == "add_image":
            image_form = PortfolioImageForm(request.POST, request.FILES)
            if image_form.is_valid():
                portfolio_image = image_form.save(commit=False)
                portfolio_image.photographer = photographer
                portfolio_image.save()
                messages.success(request, "Portfolio image added.")
                return redirect("photographer_dashboard")
        elif action == "add_project":
            project_form = PhotographerProjectForm(request.POST, request.FILES)
            if project_form.is_valid():
                project = project_form.save(commit=False)
                project.photographer = photographer
                project.save()
                messages.success(request, "Project added.")
                return redirect("photographer_dashboard")
        elif action == "add_offer":
            offer_form = PhotographerOfferForm(request.POST)
            if offer_form.is_valid():
                offer = offer_form.save(commit=False)
                offer.photographer = photographer
                offer.save()
                messages.success(request, "Offer added to your public profile.")
                return redirect("photographer_dashboard")

    return render(request, "accounts/dashboard.html", {
        "photographer": photographer,
        "profile_form": profile_form,
        "kyc_form": kyc_form,
        "image_form": image_form,
        "project_form": project_form,
        "offer_form": offer_form,
        "portfolio_images": photographer.portfolio_images.all(),
        "projects": photographer.projects.all(),
        "offers": photographer.offers.all(),
        "booking_requests": photographer.booking_requests.all(),
        "saved_photographers": request.user.saved_photographers.select_related("photographer").all(),
    })
