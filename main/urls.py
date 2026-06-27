from django.urls import path
from . import views

urlpatterns = [
    path("",views.home, name="home"),
    path("about/",views.about, name="about"),
    path("photographer_profile/",views.profile_photographer, name="photographer_profile"),
]