from django.contrib import admin
from django.urls import path, re_path

from . import views

urlpatterns = [
    path("", views.Root.as_view(), name="root"),
    path("api/athlete-details/", views.AthleteDetails.as_view(), name="athlete-details"),
    path("api/athlete-scores/", views.AthleteScores.as_view(), name="athlete-scores"),
    path("api/available-events/", views.AvailableEvents.as_view(), name="available-events"),
    path("api/handicap/", views.Handicap.as_view(), name="handicap"),
    path("api/submit/", views.Submit.as_view(), name="submit"),
    path("api/contact/", views.Contact.as_view(), name="contact"),
    path("admin/", admin.site.urls),
]
