from django.core.management.base import BaseCommand

from junior_rankings.models import AthleteSeason


class Command(BaseCommand):
    help = "Update Handicaps"

    def add_arguments(self, parser):
        parser.add_argument("agb_no", type=int, nargs="*")

    def handle(self, *args, **options):
        if options["agb_no"]:
            for agb_no in options["agb_no"]:
                season = AthleteSeason.objects.get(athlete__agb_number=agb_no)
                self.handle_row(season)
        else:
            self.stdout.write("Updating all athletes")
            for season in AthleteSeason.objects.all():
                self.handle_row(season)

    def handle_row(self, season):
        self.stdout.write("Updating Archery GB Number %s" % season.athlete.agb_number)
        season.set_agg_handicap()
        season.save()
        self.stdout.write("Aggregate handicap: %s" % season.agg_handicap)
