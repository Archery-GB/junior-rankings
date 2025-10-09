from django.contrib import admin
from django.urls import path, re_path

from . import views

urlpatterns = [
    path("", views.Root.as_view(), name="root"),
    path("admin/", admin.site.urls),
]
