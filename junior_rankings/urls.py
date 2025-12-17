from django.contrib import admin
from django.urls import path

from . import views

urlpatterns = [
    path("", views.Root.as_view(), name="root"),
    path("rankings/", views.Rankings.as_view(), name="rankings"),
    path(
        "rankings/u<int:age><slug:division>/",
        views.Rankings.as_view(),
        name="age_division_rankings",
    ),
    path(
        "rankings/<slug:division>/", views.Rankings.as_view(), name="division_rankings"
    ),
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
    path(
        "api/submission-details/",
        views.SubmissionDetails.as_view(),
        name="submission-details",
    ),
    path("api/verify-scores/", views.VerifyScores.as_view(), name="verify-scores"),
    path("admin/", admin.site.urls),
]
