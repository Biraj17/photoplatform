
from django.contrib import admin
from django.urls import path, include
from accounts.views import photographer_join

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('accounts/', include('accounts.urls')),
    path('photographer_join/', photographer_join, name='photographer_join_page'),
]