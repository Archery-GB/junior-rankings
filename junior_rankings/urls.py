from django.contrib import admin
from django.urls import path

from . import views

urlpatterns = [
    path("", views.Root.as_view(), name="root"),
    path("verify/", views.Verify.as_view(), name="verify"),
    path(
        "api/athlete-details/", views.AthleteDetails.as_view(), name="athlete-details"
    ),
    path("api/athlete-scores/", views.AthleteScores.as_view(), name="athlete-scores"),
    path(
        "api/available-events/",
        views.AvailableEvents.as_view(),
        name="available-events",
    ),
    path("api/handicap/", views.Handicap.as_view(), name="handicap"),
    path("api/submit/", views.Submit.as_view(), name="submit"),
    path("api/contact/", views.Contact.as_view(), name="contact"),
    path(
        "api/scores-to-verify/", views.ScoresToVerify.as_view(), name="scores-to-verify"
    ),
    path("admin/", admin.site.urls),
]
