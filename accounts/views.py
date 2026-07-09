import secrets
import time

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.shortcuts import redirect, render
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme

from main.emails import send_booking_decision_email
from main.forms import PhotographerOfferForm
from main.models import BookingRequest

from .emails import send_signup_otp_email
from .forms import (
    PhotographerJoinForm,
    PhotographerKYCForm,
    PhotographerLoginForm,
    PhotographerProfileForm,
    PhotographerProjectForm,
    PortfolioImageForm,
    SignupOTPForm,
)
from .models import Photographer

PENDING_SIGNUP_SESSION_KEY = "pending_signup"
OTP_TTL_SECONDS = 10 * 60
OTP_RESEND_COOLDOWN_SECONDS = 60
OTP_MAX_ATTEMPTS = 5


def register(request):
    # The old register page was an empty shell; photographers sign up
    # through the join flow.
    return redirect("photographer_join_page")


def _generate_otp():
    return f"{secrets.randbelow(1_000_000):06d}"


def _start_pending_signup(request, full_name, email, password):
    code = _generate_otp()
    if not send_signup_otp_email(email, full_name, code):
        return False
    request.session[PENDING_SIGNUP_SESSION_KEY] = {
        "full_name": full_name,
        "email": email,
        "password_hash": make_password(password),
        "otp_hash": make_password(code),
        "expires_at": time.time() + OTP_TTL_SECONDS,
        "last_sent_at": time.time(),
        "attempts": 0,
    }
    return True


def photographer_join(request):
    form = PhotographerJoinForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        sent = _start_pending_signup(
            request,
            form.cleaned_data["full_name"],
            form.cleaned_data["email"],
            form.cleaned_data["password"],
        )
        if sent:
            return redirect("verify_signup_email")
        form.add_error(
            "email",
            "We couldn't send a verification code to this address. "
            "Please check the email and try again.",
        )

    return render(request, "accounts/photographer_join.html", {
        "form": form,
    })


def verify_signup_email(request):
    pending = request.session.get(PENDING_SIGNUP_SESSION_KEY)
    if not pending:
        messages.info(request, "Start by filling in the join form — we'll email you a verification code.")
        return redirect("photographer_join_page")

    form = SignupOTPForm(request.POST or None)

    if request.method == "POST":
        if request.POST.get("action") == "resend":
            if time.time() - pending["last_sent_at"] < OTP_RESEND_COOLDOWN_SECONDS:
                messages.info(request, "Please wait a minute before requesting a new code.")
                return redirect("verify_signup_email")
            code = _generate_otp()
            if send_signup_otp_email(pending["email"], pending["full_name"], code):
                pending.update({
                    "otp_hash": make_password(code),
                    "expires_at": time.time() + OTP_TTL_SECONDS,
                    "last_sent_at": time.time(),
                    "attempts": 0,
                })
                request.session[PENDING_SIGNUP_SESSION_KEY] = pending
                messages.success(request, f"A new code was sent to {pending['email']}.")
            else:
                messages.error(request, "We couldn't send the code. Please try again in a moment.")
            return redirect("verify_signup_email")

        if form.is_valid():
            if time.time() > pending["expires_at"]:
                form.add_error("code", "This code has expired. Request a new one below.")
            elif pending["attempts"] >= OTP_MAX_ATTEMPTS:
                form.add_error("code", "Too many wrong attempts. Request a new code below.")
            elif not check_password(form.cleaned_data["code"], pending["otp_hash"]):
                pending["attempts"] += 1
                request.session[PENDING_SIGNUP_SESSION_KEY] = pending
                remaining = OTP_MAX_ATTEMPTS - pending["attempts"]
                if remaining > 0:
                    form.add_error("code", f"That code isn't right. {remaining} attempt(s) left.")
                else:
                    form.add_error("code", "Too many wrong attempts. Request a new code below.")
            else:
                try:
                    user = User(
                        username=pending["email"],
                        email=pending["email"],
                        password=pending["password_hash"],
                    )
                    user.save()
                except IntegrityError:
                    del request.session[PENDING_SIGNUP_SESSION_KEY]
                    messages.error(request, "An account with this email was just created. Try logging in instead.")
                    return redirect("photographer_login")
                Photographer.objects.create(
                    user=user,
                    full_name=pending["full_name"],
                    contact_email=pending["email"],
                )
                del request.session[PENDING_SIGNUP_SESSION_KEY]
                login(request, user, backend="django.contrib.auth.backends.ModelBackend")
                messages.success(request, "Email verified — your account is ready. Add your contact details and work here.")
                return redirect("photographer_dashboard")

    return render(request, "accounts/verify_email.html", {
        "form": form,
        "email": pending["email"],
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
        elif action == "delete_project":
            deleted, _ = photographer.projects.filter(pk=request.POST.get("project_id")).delete()
            if deleted:
                messages.success(request, "Project removed.")
            return redirect("photographer_dashboard")
        elif action == "add_offer":
            offer_form = PhotographerOfferForm(request.POST)
            if offer_form.is_valid():
                offer = offer_form.save(commit=False)
                offer.photographer = photographer
                offer.save()
                messages.success(request, "Offer added to your public profile.")
                return redirect("photographer_dashboard")
        elif action == "delete_offer":
            deleted, _ = photographer.offers.filter(pk=request.POST.get("offer_id")).delete()
            if deleted:
                messages.success(request, "Offer cancelled.")
            return redirect("photographer_dashboard")
        elif action == "dismiss_new_bookings":
            photographer.booking_requests.filter(
                status=BookingRequest.STATUS_PENDING, is_read=False
            ).update(is_read=True)
            return redirect("photographer_dashboard")
        elif action in ("accept_booking", "reject_booking"):
            booking = photographer.booking_requests.filter(pk=request.POST.get("booking_id")).first()
            if booking:
                accepted = action == "accept_booking"
                booking.status = BookingRequest.STATUS_ACCEPTED if accepted else BookingRequest.STATUS_REJECTED
                booking.responded_at = timezone.now()
                booking.is_read = True
                booking.save()
                send_booking_decision_email(booking, accepted=accepted)
                messages.success(
                    request,
                    f"Booking {'accepted' if accepted else 'declined'}. "
                    f"{booking.client_name} has been notified by email.",
                )
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
        "booking_requests": photographer.booking_requests.filter(status=BookingRequest.STATUS_PENDING),
        "new_booking_requests": photographer.booking_requests.filter(
            status=BookingRequest.STATUS_PENDING, is_read=False
        ),
        "booking_history": photographer.booking_requests.exclude(
            status=BookingRequest.STATUS_PENDING
        ).order_by("-responded_at"),
        "saved_photographers": request.user.saved_photographers.select_related("photographer").all(),
    })
