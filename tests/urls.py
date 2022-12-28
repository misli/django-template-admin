from django.contrib import admin

try:
    from django.urls import path
except ImportError:
    # Django<2
    from django.conf.urls import url as path

urlpatterns = [
    path("admin/", admin.site.urls),
]
