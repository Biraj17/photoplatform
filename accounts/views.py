from django.shortcuts import render

from .forms import PhotographerJoinForm


def register(request):
    return render(request, "accounts/register.html")


def photographer_join(request):
    success = False
    form = PhotographerJoinForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        success = True
        form = PhotographerJoinForm()

    return render(request, "accounts/photographer_join.html", {
        "form": form,
        "success": success,
    })
