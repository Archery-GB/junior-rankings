from django.conf import settings
from django.contrib import admin, messages

import requests
from django_object_actions import DjangoObjectActions, action

from archerydjango.fields import DbBowstyles, DbGender
from archerydjango.utils import get_age_group

from .allowed_rounds import get_allowed_rounds
from .models import (
    Season,
    Athlete,
    AthleteSeason,
    Event,
    Score,
    Submission,
    SubmissionScore,
    ContactResponse,
)


@admin.register(Athlete)
class AthleteAdmin(admin.ModelAdmin):
    list_display = ["name", "agb_number"]
    search_fields = ["forename", "surname", "agb_number"]


@admin.register(Event)
class EventAdmin(DjangoObjectActions, admin.ModelAdmin):
    list_display = ["name", "date", "round_family"]
    list_filter = ["date", "round_family"]
    search_fields = ["name"]
    change_actions = ["import_scores"]

    @action(label="Import scores", description="Import scores from AGB extranet")
    def import_scores(self, request, obj):
        if not obj.extranet_id:
            self.message_user(request, "Cannot import scores: Event has no extranet ID.", messages.ERROR)
            return

        try:
            response = requests.get(
                "https://records.agbextranet.org.uk/Public/ShootReturn.php",
                params={"SHOOTCODE": obj.extranet_id},
            )
        except:
            self.message_user(request, "Cannot import scores: Something went wrong accessing the Extranet API", messages.ERROR)
            return

        data = response.json()["value"]
        if not len(data):
            self.message_user(request, "Cannot import scores: No scores received from API", messages.ERROR)
            return

        if Score.objects.filter(event=obj).exists():
            self.message_user(request, "Cannot import scores: Already have scores for this event.", messages.ERROR)
            return

        total_created = 0
        season = Season.objects.get(year=obj.date.year)

        for record in data:
            if record["Score"] == "0":
                # Skip athletes with a score of 0 as DNS
                continue

            athlete_data = {}
            athlete_data["agb_number"] = record["AthID"]
            athlete_data["gender"] = DbGender.__lookup__[record["Code"][-1]]
            athlete_data["bowstyle"] = DbBowstyles.__lookup__[record["Code"][0]]
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
                
                athlete = Athlete.objects.create(
                    agb_number=athlete_data["agb_number"],
                    forename=athlete_data["forename"],
                    surname=athlete_data["surname"],
                    year=athlete_data["year"],
                    gender=athlete_data["gender"],
                )

            athlete_data["age_group"] = get_age_group(athlete.year, obj.date.year)
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

            athlete_data["shot_round"] = get_allowed_rounds(
                family=obj.round_family,
                gender=athlete_data["gender"],
                age_group=athlete_data["age_group"],
                bowstyle=athlete_data["bowstyle"],
            )[0]

            Score.objects.create(
                athlete_season=athlete_season,
                event=obj,
                shot_round=athlete_data["shot_round"],
                score=athlete_data["score"],
            )

            total_created += 1

        self.message_user(request, "%s new scores imported" % total_created, messages.SUCCESS)



admin.site.register(Season)
admin.site.register(AthleteSeason)
admin.site.register(Score)
admin.site.register(Submission)
admin.site.register(SubmissionScore)
admin.site.register(ContactResponse)
