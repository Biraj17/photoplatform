from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("photographers/", views.photographers_list, name="photographers_list"),
    path("offers/", views.offers_list, name="offers_list"),
    path("photographer_profile/", views.profile_photographer, name="photographer_profile"),
]