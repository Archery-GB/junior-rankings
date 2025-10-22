from django.core import validators
from django.db import models

import archeryutils

from archerydjango.fields import (
    AgeField,
    BowstyleField,
    GenderField,
    RoundField,
)


class Season(models.Model):
    year = models.PositiveIntegerField(
        validators=[
            validators.MinValueValidator(2000),
            validators.MaxValueValidator(2100),
        ]
    )

    def __str__(self):
        return "%s season" % self.year

    class Meta:
        ordering = ["-year"]


class Athlete(models.Model):
    agb_number = models.CharField(max_length=256)
    forename = models.CharField(max_length=256)
    surname = models.CharField(max_length=256)
    year = models.PositiveIntegerField(
        "Year of Birth",
        validators=[
            validators.MinValueValidator(2000),
            validators.MaxValueValidator(2100),
        ],
    )
    gender = GenderField()

    def __str__(self):
        return "%s %s" % (self.forename, self.surname)


class AthleteSeason(models.Model):
    athlete = models.ForeignKey(Athlete, on_delete=models.PROTECT)
    season = models.ForeignKey(Season, on_delete=models.PROTECT)
    age_group = AgeField()
    bowstyle = BowstyleField()

    # Rank
    # Rank is equal
    # Aggregate handicap

    def __str__(self):
        return "%s in %s" % (self.athlete, self.season)


class Event(models.Model):
    identifier = models.CharField(max_length=256)
    name = models.CharField(max_length=512)
    date = models.DateField()  # First day for multi-day events
    round_family = models.CharField(max_length=64)

    def __str__(self):
        return self.name


class Score(models.Model):
    athlete_season = models.ForeignKey(AthleteSeason, on_delete=models.PROTECT)
    event = models.ForeignKey(Event, on_delete=models.PROTECT)
    shot_round = RoundField(
        rounds=(
            archeryutils.load_rounds.WA_outdoor
            | archeryutils.load_rounds.AGB_outdoor_metric
            | archeryutils.load_rounds.AGB_outdoor_imperial
        )
    )
    score = models.PositiveIntegerField()

    def __str__(self):
        return "%s shot %s on %s at %s" % (
            self.athlete_season.athlete,
            self.score,
            self.shot_round,
            self.score,
        )


###
# One day, we delete everything below here because we have all scores digitally
##


class Submission(models.Model):
    agb_number = models.CharField(max_length=256)
    forename = models.CharField(max_length=256)
    surname = models.CharField(max_length=256)
    year = models.PositiveIntegerField(
        "Year of Birth",
        validators=[
            validators.MinValueValidator(2000),
            validators.MaxValueValidator(2100),
        ],
    )
    gender = GenderField()
    bowstyle = BowstyleField()


class SubmissionScore(models.Model):
    submission = models.ForeignKey(Submission, on_delete=models.PROTECT)
    event = models.ForeignKey(Event, on_delete=models.PROTECT)
    shot_round = RoundField(
        rounds=(
            archeryutils.load_rounds.WA_outdoor
            | archeryutils.load_rounds.AGB_outdoor_metric
            | archeryutils.load_rounds.AGB_outdoor_imperial
        )
    )
    score = models.PositiveIntegerField()
