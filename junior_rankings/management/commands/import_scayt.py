import json

import requests
from django.conf import settings
from django.core.management.base import BaseCommand

from archerydjango.fields import DbBowstyles
from archerydjango.utils import get_age_group
from junior_rankings.allowed_rounds import all_rounds, get_allowed_rounds
from junior_rankings.models import Athlete, AthleteSeason, Event, Score, Season


class Command(BaseCommand):
    help = "Import SCAYT data from a JSON file"

    def add_arguments(self, parser):
        parser.add_argument("filename", type=str)

    def handle(self, *args, **options):
        with open(options["filename"]) as f:
            data = json.loads(f.read())

        event_lookup = {
            "Sussex Junior Championships": 42693,
            "Wallingford Good Friday 720": 42334,
            "SCAS Junior Championships & SCAYT Final": 42333,
            "Wallingford Junior Matchplay": 42335,
            "Noak Hill Double 720": 42098,
            "Buckinghamshire Championships": 42309,
            "Woking Open": 42457,
            "Essex Target Championships": 42170,
            "Wallingford Summer Metrics": 42337,
            "Oxfordshire Junior Championships": 42340,
            "Harlequin 60th Diana Shoot": 41954,
            "Andover Archers Saxon Shoot": 42047,
            "SCCA Junior 900": 42489,
            "Hillingdon 2 Day Double 720 - Day 1": 41650,
            "Peacock World Archery Weekend - Day 2": 42153,
            "Wymondham WA Weekend - Day 1": 41887,
            "Forest of Bere Bowmen Open": 41879,
            "Berkshire Championships": 42297,
            "Oxfordshire Outdoor Championships": 42336,
            "Rayleigh Town 720": 42406,
            "Wymondham WA Weekend - Day 2": 41888,
            "Whiteleaf Bowmen Open": 42308,
            "Hillingdon 2 Day Double 720 - Day 2": "41650-2",
            "Wallingford Castle Archers 720": 42338,
            "Essex WA1440 Championship": 42526,
        }

        season = Season.objects.order_by("-year").first()

        for s in data:
            if s["event"] not in event_lookup:
                continue
            event = Event.objects.get(identifier=event_lookup[s["event"]])

            try:
                athlete_season = AthleteSeason.objects.get(
                    athlete__agb_number=s["agb_number"], bowstyle=s["bowstyle"]
                )
                athlete = athlete_season.athlete
            except AthleteSeason.DoesNotExist:
                response = requests.get(
                    "https://records.agbextranet.org.uk/Public/AGBLookup.php",
                    params={"agbno": s["agb_number"]},
                    headers={"Authorization": "Bearer %s" % settings.AGB_API_TOKEN},
                )
                api_athlete = response.json()["results"][0]
                athlete = Athlete(
                    agb_number=s["agb_number"],
                    forename=api_athlete["Firstname"],
                    surname=api_athlete["Lastname"],
                    year=int(api_athlete["YOB"]),
                    gender=s["gender"],
                )
                athlete_season = AthleteSeason(
                    athlete=athlete,
                    bowstyle=DbBowstyles(s["bowstyle"]),
                    season=season,
                    age_group=get_age_group(athlete.year, event.date.year),
                )

            allowed_rounds = get_allowed_rounds(
                family=event.round_family,
                gender=athlete.gender,
                age_group=athlete_season.age_group,
                bowstyle=athlete_season.bowstyle,
            )
            if all_rounds[s["round"]] not in allowed_rounds:
                continue

            athlete.save()
            athlete_season.save()
            Score.objects.create(
                athlete_season=athlete_season,
                event=event,
                score=s["score"],
                shot_round=s["round"],
            )
