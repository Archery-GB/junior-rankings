import json

from django.http.response import JsonResponse
from django.utils import timezone
from django.views.generic import TemplateView, View

from archeryutils.handicaps import handicap_from_score
from braces.views import CsrfExemptMixin, LoginRequiredMixin

from .allowed_rounds import all_available_rounds, get_allowed_rounds
from .models import (
    AthleteSeason,
    ContactResponse,
    Event,
    Submission,
    SubmissionScore,
)


class Root(TemplateView):
    template_name = "junior_rankings/root.html"

    def get_context_data(self, **kwargs):
        return super().get_context_data(page_name="root", **kwargs)


class Verify(LoginRequiredMixin, TemplateView):
    template_name = "junior_rankings/verify.html"

    def get_context_data(self, **kwargs):
        return super().get_context_data(page_name="verify", **kwargs)


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
                    for score in sorted(scores, key=lambda s: (s.handicap, -s.score))
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
            handicap = self.calculate_handicap()
        except ResponseException as e:
            return e.response
        return JsonResponse({"handicap": handicap})

    def calculate_handicap(self):
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


class Submit(CsrfExemptMixin, View):
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


class Contact(CsrfExemptMixin, View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        ContactResponse.objects.create(
            email=data["email"],
            agb_number=data["agbNo"],
            message=data["message"],
        )
        return JsonResponse({"status": "ok"})


class ScoresToVerify(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        submissions = (
            Submission.objects.filter(
                processed__isnull=True,
            )
            .select_related("athlete_season", "athlete_season__athlete")
            .prefetch_related(
                "submissionscore_set",
                "submissionscore_set__event",
                "athlete_season__score_set",
                "athlete_season__score_set__event",
            )
        )

        data = {}
        for sub in submissions:
            athlete_season = sub.athlete_season
            athlete = athlete_season.athlete
            if athlete_season.id not in data:
                data[athlete_season.id] = {
                    "id": athlete_season.id,
                    "agbNo": athlete.agb_number,
                    "name": athlete.name,
                    "gender": athlete.gender.label,
                    "age": athlete_season.age_group.label,
                    "division": athlete_season.bowstyle.label,
                }
        to_verify = sorted(
            data.values(),
            key=lambda a: (a["division"], a["gender"], a["age"], a["agbNo"]),
        )
        return JsonResponse({"status": "ok", "toVerify": to_verify})


class SubmissionDetails(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        try:
            season = AthleteSeason.objects.get(pk=request.GET["id"])
        except (AthleteSeason.DoesNotExist, KeyError):
            return JsonResponse(
                {"status": "error", "message": "Season not found"}, status=404
            )
        scores = [
            {
                "id": "checked:%s" % score.id,
                "score": score.score,
                "event": score.event.name,
                "date": score.event.date,
                "round": score.shot_round.name,
                "handicap": score.handicap,
                "verified": True,
            }
            for score in sorted(season.score_set.all(), key=lambda s: s.handicap)
        ]

        submitted = sorted(
            SubmissionScore.objects.filter(submission__athlete_season=season).all(),
            key=lambda s: s.handicap,
        )
        new_scores = [
            {
                "id": score.id,
                "score": score.score,
                "event": score.event.name,
                "date": score.event.date,
                "round": score.shot_round.name,
                "handicap": score.handicap,
                "verified": False,
            }
            for score in submitted
        ]

        return JsonResponse({"status": "ok", "scores": scores, "newScores": new_scores})


class VerifyScores(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        for score in data["scores"]:
            submission_score = SubmissionScore.objects.get(id=score["id"])
            submission = submission_score.submission
            athlete_season = submission.athlete_season
            if score["accept"]:
                submission_score.accepted = timezone.now()
                athlete_season.score_set.create(
                    event=submission_score.event,
                    shot_round=submission_score.shot_round,
                    score=submission_score.score,
                )
            else:
                submission_score.rejected = timezone.now()
            submission.processed = timezone.now()
            submission.save()
            submission_score.save()
        if not data["scores"]:
            Submission.objects.filter(athlete_season_id=data["id"]).update(processed=timezone.now())
        return JsonResponse({"status": "ok"})
