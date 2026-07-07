from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("photographers/", views.photographers_list, name="photographers_list"),
    path("photographers/<int:pk>/", views.profile_photographer, name="photographer_profile_detail"),
    path("photographers/<int:pk>/save/", views.toggle_saved_photographer, name="toggle_saved_photographer"),
    path("offers/", views.offers_list, name="offers_list"),
    path("photographer_profile/", views.profile_photographer, name="photographer_profile"),
    path("pages/<slug:slug>/", views.info_page, name="info_page"),
]
