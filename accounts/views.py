from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import (
    PhotographerJoinForm,
    PhotographerLoginForm,
    PhotographerProfileForm,
    PhotographerProjectForm,
    PortfolioImageForm,
)
from .models import Photographer


def register(request):
    return render(request, "accounts/register.html")


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

    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        return redirect("photographer_dashboard")

    return render(request, "accounts/login.html", {
        "form": form,
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
    image_form = PortfolioImageForm()
    project_form = PhotographerProjectForm()

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "save_profile":
            profile_form = PhotographerProfileForm(request.POST, request.FILES, instance=photographer)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, "Profile details updated.")
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

    return render(request, "accounts/dashboard.html", {
        "photographer": photographer,
        "profile_form": profile_form,
        "image_form": image_form,
        "project_form": project_form,
        "portfolio_images": photographer.portfolio_images.all(),
        "projects": photographer.projects.all(),
    })
