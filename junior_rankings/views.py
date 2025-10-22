import itertools

from django.db.models import Count
from django.http.response import JsonResponse
from django.views.generic import TemplateView, View
from django.utils import timezone

from .models import AthleteSeason


class Root(TemplateView):
    template_name = "junior_rankings/root.html"

    def get_context_data(self, **kwargs):
        return super().get_context_data(page_name="root", **kwargs)


class AthleteDetails(View):
    def get(self, request, *args, **kwargs):
        if "agb_number" not in self.request.GET:
            return JsonResponse({
                "error": "Missing parameter: agb_number",
            }, status=400)
        try:
            athlete_season = AthleteSeason.objects.get(season__year=2025, athlete__agb_number=request.GET["agb_number"]);
        except AthleteSeason.DoesNotExist:
            return JsonResponse({
                "error": "Athlete not found",
            }, status=404)
        athlete = athlete_season.athlete
        return JsonResponse({
            "agbNo": athlete.agb_number,
            "name": athlete.name,
            "year": athlete.year,
            "gender": athlete.gender.label,
            "age": athlete_season.age_group.label,
            "division": athlete_season.bowstyle.label,
        });


class AthleteScores(View):
    def get(self, request, *args, **kwargs):
        if "agb_number" not in self.request.GET:
            return JsonResponse({
                "error": "Missing parameter: agb_number",
            }, status=400)
        try:
            athlete_season = AthleteSeason.objects.get(season__year=2025, athlete__agb_number=request.GET["agb_number"]);
        except AthleteSeason.DoesNotExist:
            return JsonResponse({
                "error": "Athlete not found",
            }, status=404)
        scores = athlete_season.score_set.all()
        return JsonResponse({
            "scores": [{
                "score": score.score,
                "round": score.shot_round.name,
                "event": score.event.name,
                "eventId": score.event.identifier,
                "date": score.event.date,
                "handicap": score.handicap,
            } for score in sorted(scores, key=lambda s: s.handicap)]
        });
