import json

from archeryutils.handicaps import handicap_from_score
from django.http.response import JsonResponse
from django.views.generic import TemplateView, View

from .allowed_rounds import all_available_rounds, get_allowed_rounds
from .models import (AthleteSeason, ContactResponse, Event, Submission,
                     SubmissionScore)


class Root(TemplateView):
    template_name = "junior_rankings/root.html"

    def get_context_data(self, **kwargs):
        return super().get_context_data(page_name="root", **kwargs)


class ResponseException(Exception):
    def __init__(self, message, status):
        super().__init__(message)
        self.response = JsonResponse(
            {
                "error": message,
            },
            status=status,
        )


class AthleteSeasonByAgbNo(object):
    def load_athlete_season(self):
        if "agb_number" not in self.request.GET:
            raise ResponseException("Missing parameter: agb_number", 400)
        try:
            athlete_season = AthleteSeason.objects.get(
                season__year=2025, athlete__agb_number=self.request.GET["agb_number"]
            )
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
        return JsonResponse(
            {
                "agbNo": athlete.agb_number,
                "name": athlete.name,
                "gender": athlete.gender.label,
                "age": athlete_season.age_group.label,
                "division": athlete_season.bowstyle.label,
            }
        )


class AthleteScores(AthleteSeasonByAgbNo, View):
    def get(self, request, *args, **kwargs):
        try:
            athlete_season = self.load_athlete_season()
        except ResponseException as e:
            return e.response
        scores = athlete_season.score_set.all()
        return JsonResponse(
            {
                "scores": [
                    {
                        "id": score.pk,
                        "score": score.score,
                        "round": score.shot_round.name,
                        "event": score.event.name,
                        "eventId": score.event.identifier,
                        "date": score.event.date,
                        "handicap": score.handicap,
                    }
                    for score in sorted(scores, key=lambda s: s.handicap)
                ]
            }
        )


class AvailableEvents(AthleteSeasonByAgbNo, View):
    def get(self, request, *args, **kwargs):
        try:
            athlete_season = self.load_athlete_season()
        except ResponseException as e:
            return e.response
        events = Event.objects.exclude(score__athlete_season=athlete_season).order_by(
            "date"
        )
        return JsonResponse(
            {
                "events": [
                    {
                        "identifier": event.identifier,
                        "name": event.name,
                        "date": event.date,
                        "rounds": [
                            {
                                "codename": r.codename,
                                "name": r.name,
                            }
                            for r in get_allowed_rounds(
                                event.round_family,
                                athlete_season.athlete.gender,
                                athlete_season.age_group,
                                athlete_season.bowstyle,
                            )
                        ],
                    }
                    for event in events
                ]
            }
        )


class Handicap(View):
    def get(self, request, *args, **kwargs):
        try:
            handicap = self.calulcate_handicap()
        except ResponseException as e:
            return e.response
        return JsonResponse({"handicap": handicap})

    def calulcate_handicap(self):
        if "round" not in self.request.GET:
            raise ResponseException("Missing parameter: round", 400)
        if "score" not in self.request.GET:
            raise ResponseException("Missing parameter: score", 400)
        if self.request.GET["round"] not in all_available_rounds:
            raise ResponseException("Invalid parameter: round", 400)
        try:
            score = int(self.request.GET["score"])
        except ValueError:
            raise ResponseException("Invalid parameter: score", 400)
        rnd = all_available_rounds[self.request.GET["round"]]
        try:
            return handicap_from_score(score, rnd, "AGB", int_prec=True)
        except ValueError:
            raise ResponseException("Invalid score", 400)


class Submit(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        # FIXME This will break if anyone has double bow styles but there aren't any (yet!)
        athlete_season = AthleteSeason.objects.get(
            athlete__agb_number=data["agbNo"],
            season__year=2025,
        )
        submission = Submission.objects.create(athlete_season=athlete_season)
        for score in data["scores"]:
            event = Event.objects.get(identifier=score["event"])
            SubmissionScore.objects.create(
                submission=submission,
                event=event,
                shot_round=score["round"],
                score=score["score"],
            )
        return JsonResponse({"status": "ok"})


class Contact(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        ContactResponse.objects.create(
            email=data["email"],
            agb_number=data["agbNo"],
            message=data["message"],
        )
        return JsonResponse({"status": "ok"})
