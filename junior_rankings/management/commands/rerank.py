import itertools

from django.core.management.base import BaseCommand

from archerydjango.fields import DbAges, DbBowstyles, DbGender
from junior_rankings.models import AthleteSeason


class Command(BaseCommand):
    help = "Re rank all athletes"

    def handle(self, *args, **options):
        for bow, gender in itertools.product(DbBowstyles, DbGender):
            self.stdout.write("Ranking %s %s" % (bow, gender))
            seasons = AthleteSeason.objects.filter(
                bowstyle=bow, athlete__gender=gender, agg_handicap__isnull=False
            ).order_by("agg_handicap")
            self.stdout.write("%s athletes" % seasons.count())

            current_rank = 0
            current_hc = None
            prev = None
            skip = 0
            for season in seasons:
                if season.agg_handicap != current_hc:
                    current_rank = current_rank + 1 + skip
                    current_hc = season.agg_handicap
                    skip = 0
                else:
                    season.overall_rank_is_equal = True
                    prev.overall_rank_is_equal = True
                    prev.save()
                    skip += 1
                season.overall_rank = current_rank
                season.save()
                prev = season

        for bow, age, gender in itertools.product(
            DbBowstyles, list(DbAges)[2:], DbGender
        ):
            self.stdout.write("Ranking %s %s %s" % (age, bow, gender))
            seasons = AthleteSeason.objects.filter(
                bowstyle=bow,
                age_group=age,
                athlete__gender=gender,
                agg_handicap__isnull=False,
            ).order_by("agg_handicap")
            self.stdout.write("%s athletes" % seasons.count())

            current_rank = 0
            current_hc = None
            prev = None
            skip = 0
            for season in seasons:
                if season.agg_handicap != current_hc:
                    current_rank = current_rank + 1 + skip
                    current_hc = season.agg_handicap
                    skip = 0
                else:
                    season.age_group_rank_is_equal = True
                    prev.age_group_rank_is_equal = True
                    prev.save()
                    skip += 1
                season.age_group_rank = current_rank
                season.save()
                prev = season
