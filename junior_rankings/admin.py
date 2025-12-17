from django.conf import settings
from django.contrib import admin, messages
from django.db import transaction

import requests
from django_object_actions import DjangoObjectActions, action

from archerydjango.fields import DbAges, DbBowstyles, DbGender
from archerydjango.utils import get_age_group

from .allowed_rounds import all_rounds, get_allowed_rounds
from .models import (
    Athlete,
    AthleteSeason,
    ContactResponse,
    Event,
    Score,
    Season,
    Submission,
    SubmissionScore,
)


@admin.register(Athlete)
class AthleteAdmin(admin.ModelAdmin):
    list_display = ["name", "agb_number"]
    search_fields = ["forename", "surname", "agb_number"]


@admin.register(Event)
class EventAdmin(DjangoObjectActions, admin.ModelAdmin):
    list_display = ["name", "identifier", "date", "round_family"]
    list_filter = ["date", "round_family"]
    search_fields = ["name"]
    change_actions = ["import_scores"]

    @action(label="Import scores", description="Import scores from AGB extranet")
    @transaction.atomic
    def import_scores(self, request, obj):
        if not obj.extranet_id:
            self.message_user(
                request,
                "Cannot import scores: Event has no extranet ID.",
                messages.ERROR,
            )
            return

        try:
            response = requests.get(
                "https://records.agbextranet.org.uk/Public/ShootReturn.php",
                params={"SHOOTCODE": obj.extranet_id},
            )
        except:
            self.message_user(
                request,
                "Cannot import scores: Something went wrong accessing the Extranet API",
                messages.ERROR,
            )
            return

        data = response.json()["value"]
        if not len(data):
            self.message_user(
                request,
                "Cannot import scores: No scores received from API",
                messages.ERROR,
            )
            return

        if Score.objects.filter(event=obj).exists():
            self.message_user(
                request,
                "Cannot import scores: Already have scores for this event.",
                messages.ERROR,
            )
            return

        total_created = 0
        season = Season.objects.get(year=obj.date.year)

        for record in data:
            if record["Score"] == "0":
                # Skip athletes with a score of 0 as DNS
                continue
            if record["AthID"] == "0":
                # Skip athletes with a missing AGB Number
                continue
            if not (
                record["Category"].endswith("M") or record["Category"].endswith("W")
            ):
                # Skip records with e.g. RMLD?
                continue

            athlete_data = {}
            athlete_data["agb_number"] = record["AthID"]
            athlete_data["gender"] = DbGender.__lookup__[record["Category"][-1]]
            athlete_data["bowstyle"] = DbBowstyles.__lookup__[record["Category"][0]]
            athlete_data["score"] = record["Score"]

            try:
                athlete = Athlete.objects.get(agb_number=athlete_data["agb_number"])
            except Athlete.DoesNotExist:
                response = requests.get(
                    "https://records.agbextranet.org.uk/Public/AGBLookup.php",
                    params={"agbno": athlete_data["agb_number"]},
                    headers={"Authorization": "Bearer %s" % settings.AGB_API_TOKEN},
                )
                api_athlete = response.json()["results"][0]
                athlete_data["forename"] = api_athlete["full_name"].split(" ", 1)[0]
                athlete_data["surname"] = api_athlete["full_name"].split(" ", 1)[1]
                athlete_data["year"] = int(api_athlete["YOB"])

                athlete = Athlete(
                    agb_number=athlete_data["agb_number"],
                    forename=athlete_data["forename"],
                    surname=athlete_data["surname"],
                    year=athlete_data["year"],
                    gender=athlete_data["gender"],
                )

            athlete_data["age_group"] = get_age_group(athlete.year, obj.date.year)
            if athlete_data["age_group"] in [
                DbAges.AGE_UNDER_21,
                DbAges.AGE_UNDER_18,
                DbAges.AGE_UNDER_16,
                DbAges.AGE_UNDER_15,
                DbAges.AGE_UNDER_14,
                DbAges.AGE_UNDER_12,
            ]:
                athlete.save()
            else:
                # Skip any adult scores
                continue

            try:
                athlete_season = AthleteSeason.objects.get(
                    athlete=athlete,
                    season=season,
                    bowstyle=athlete_data["bowstyle"],
                )
            except AthleteSeason.DoesNotExist:
                athlete_season = AthleteSeason.objects.create(
                    athlete=athlete,
                    season=season,
                    age_group=athlete_data["age_group"],
                    bowstyle=athlete_data["bowstyle"],
                )

            competed_age_group = record["Category"][1:-1]
            try:
                athlete_data["competed_age_group"] = DbAges.__lookup__[
                    competed_age_group
                ]
            except KeyError:
                athlete_data["competed_age_group"] = DbAges.AGE_UNDER_21

            if not obj.round_age_rules:
                athlete_data["shot_round"] = get_allowed_rounds(
                    family=obj.round_family,
                    gender=athlete_data["gender"],
                    age_group=athlete_data["competed_age_group"],
                    bowstyle=athlete_data["bowstyle"],
                )[0]
            elif obj.round_age_rules == "jas":
                shot_round = {
                    "BY": "wa720_50_b",
                    "CY": "wa720_50_c",
                    "RU15": "metric_122_40",
                    "RU18": "wa720_60",
                    "RU21": "wa720_70",
                }[record["Category"][:-1]]
                athlete_data["shot_round"] = all_rounds[shot_round]
            elif obj.round_age_rules == "nt":
                shot_round = {
                    "B": "wa720_50_b",
                    "C": "wa720_50_c",
                    "R": "wa720_70",
                    "L": "wa720_70",
                }[record["Category"][0]]
                athlete_data["shot_round"] = all_rounds[shot_round]
            elif obj.round_age_rules == "nt-1440":
                shot_round = {
                    "M": "wa1440_90",
                    "W": "wa1440_70",
                }[record["Category"][-1]]
                athlete_data["shot_round"] = all_rounds[shot_round]

            # For now, remove duplicates. When the double rounds work, this will need some conditions!

            if Score.objects.filter(
                athlete_season=athlete_season,
                event=obj,
            ).exists():
                continue
            if "Score1" in record:
                Score.objects.create(
                    athlete_season=athlete_season,
                    event=obj,
                    shot_round=athlete_data["shot_round"],
                    score=record["Score1"],
                )
                Score.objects.create(
                    athlete_season=athlete_season,
                    event=obj,
                    shot_round=athlete_data["shot_round"],
                    score=record["Score2"],
                )
            else:
                Score.objects.create(
                    athlete_season=athlete_season,
                    event=obj,
                    shot_round=athlete_data["shot_round"],
                    score=athlete_data["score"],
                )

            total_created += 1

        self.message_user(
            request, "%s new scores imported" % total_created, messages.SUCCESS
        )


@admin.register(Score)
class ScoreAdmin(admin.ModelAdmin):
    list_display = ["score", "athlete_season__athlete", "event"]
    list_filter = ["event"]


@admin.register(AthleteSeason)
class AthleteSeasonAdmin(admin.ModelAdmin):
    list_display = [
        "athlete",
        "season",
        "age_group",
        "bowstyle",
        "agg_handicap",
        "overall_rank_display",
        "age_group_rank_display",
    ]
    list_filter = ["season", "athlete__gender", "bowstyle", "age_group"]
    search_fields = ["athlete__forename", "athlete__surname", "athlete__agb_number"]


@admin.register(ContactResponse)
class ContactResponseAdmin(admin.ModelAdmin):
    list_display = ["email", "processed", "timestamp"]


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ["athlete_season__athlete", "submitted", "processed"]
    search_fields = [
        "athlete_season__athlete__forename",
        "athlete_season__athlete__forename",
        "athlete_season__athlete__agb_number",
    ]
    readonly_fields = ["processed"]


admin.site.register(Season)
admin.site.register(SubmissionScore)
