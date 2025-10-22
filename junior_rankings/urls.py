from django.contrib import admin
from django.urls import path, re_path

from . import views

urlpatterns = [
    path("", views.Root.as_view(), name="root"),
    path("api/athlete-details/", views.AthleteDetails.as_view(), name="athlete-details"),
    path("api/athlete-scores/", views.AthleteScores.as_view(), name="athlete-scores"),
    path("admin/", admin.site.urls),
]
