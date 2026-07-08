
from django.contrib import admin
from django.conf import settings
from django.urls import path, include, re_path
from django.views.static import serve as serve_static
from accounts.views import bootstrap_admin_password, photographer_join

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('accounts/', include('accounts.urls')),
    path('photographer_join/', photographer_join, name='photographer_join_page'),
    path('bootstrap-admin-password/', bootstrap_admin_password, name='bootstrap_admin_password'),
]

# django.conf.urls.static.static() no-ops when DEBUG=False, so it's used directly
# here instead. There's no object storage backend configured yet, so media is
# served straight off local disk — fine at this project's scale; move to
# S3/Cloudinary if traffic grows.
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve_static, {'document_root': settings.MEDIA_ROOT}),
]
