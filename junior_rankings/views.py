import itertools

from django.db.models import Count
from django.http.response import JsonResponse
from django.views.generic import TemplateView, View
from django.utils import timezone

from .allowed_rounds import get_allowed_rounds
from .models import AthleteSeason, Event


class Root(TemplateView):
    template_name = "junior_rankings/root.html"

    def get_context_data(self, **kwargs):
        return super().get_context_data(page_name="root", **kwargs)


class ResponseException(Exception):
    def __init__(self, message, status):
        super().__init__(message)
        self.response = JsonResponse({
            "error": message,
        }, status=status)


class AthleteSeasonByAgbNo(object):
    def load_athlete_season(self):
        if "agb_number" not in self.request.GET:
            raise ResponseException("Missing parameter: agb_number", 400)
        try:
            athlete_season = AthleteSeason.objects.get(season__year=2025, athlete__agb_number=self.request.GET["agb_number"]);
        except AthleteSeason.DoesNotExist:
            raise ResponseException("Athlete not found", 404)
        return athlete_season


class AthleteDetails(AthleteSeasonByAgbNo, View):
    def get(self, request, *args, **kwargs):
        try:
            athlete_season = self.load_athlete_season()
        except ResponseException as e:
            return e.response
        athlete = athlete_season.athlete
        return JsonResponse({
            "agbNo": athlete.agb_number,
            "name": athlete.name,
            "year": athlete.year,
            "gender": athlete.gender.label,
            "age": athlete_season.age_group.label,
            "division": athlete_season.bowstyle.label,
        });


class AthleteScores(AthleteSeasonByAgbNo, View):
    def get(self, request, *args, **kwargs):
        try:
            athlete_season = self.load_athlete_season()
        except ResponseException as e:
            return e.response
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


class AvailableEvents(AthleteSeasonByAgbNo, View):
    def get(self, request, *args, **kwargs):
        try:
            athlete_season = self.load_athlete_season()
        except ResponseException as e:
            return e.response
        events = Event.objects.exclude(score__athlete_season=athlete_season).order_by('date')
        return JsonResponse({
            "events": [{
                "identifier": event.identifier,
                "name": event.name,
                "date": event.date,
                "rounds": [{
                    "codename": r.codename,
                    "name": r.name,
                } for r in get_allowed_rounds(event.round_family, athlete_season.athlete.gender, athlete_season.age_group, athlete_season.bowstyle)]
            } for event in events]
        });

