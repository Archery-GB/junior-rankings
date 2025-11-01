import csv

from django.core.management.base import BaseCommand

from junior_rankings.models import Event


class Command(BaseCommand):
    help = "Import events from a CSV"

    def add_arguments(self, parser):
        parser.add_argument("filename", type=str)

    def handle(self, *args, **options):
        with open(options["filename"]) as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                Event.objects.create(**row)
                self.stdout.write("Created event: %s" % row["name"])
