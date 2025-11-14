from archeryutils.handicaps import handicap_from_score
from django.core import validators
from django.db import models

from archerydjango.fields import (AgeField, BowstyleField, GenderField,
                                  RoundField)

from .allowed_rounds import all_available_rounds


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
        return self.name

    @property
    def name(self):
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
    extranet_id = models.CharField(max_length=256, blank=True, default="")
    name = models.CharField(max_length=512)
    date = models.DateField()  # First day for multi-day events
    round_family = models.CharField(max_length=64)
    round_age_rules = models.CharField(
        max_length=20,
        blank=True,
        default="",
        choices=[
            ("", "Unknown - Use shortest allowed round"),
            ("jas", "Junior Archery Series"),
            ("nt", "National Tour"),
            ("nt-1440", "National Tour (1440)"),
        ],
        help_text="To identify round by age group for imported events",
    )

    def __str__(self):
        return self.name


class Score(models.Model):
    athlete_season = models.ForeignKey(AthleteSeason, on_delete=models.PROTECT)
    event = models.ForeignKey(Event, on_delete=models.PROTECT)
    shot_round = RoundField(all_available_rounds)
    score = models.PositiveIntegerField()

    def __str__(self):
        return "%s shot %s on %s at %s" % (
            self.athlete_season.athlete,
            self.score,
            self.shot_round,
            self.score,
        )

    @property
    def handicap(self):
        return handicap_from_score(self.score, self.shot_round, "AGB", int_prec=True)


class Submission(models.Model):
    athlete_season = models.ForeignKey(AthleteSeason, on_delete=models.PROTECT)

    def __str__(self):
        return "Submission for %s" % self.athlete_season


class SubmissionScore(models.Model):
    # Additional scores submitted by the user
    submission = models.ForeignKey(Submission, on_delete=models.PROTECT)
    event = models.ForeignKey(Event, on_delete=models.PROTECT)
    shot_round = RoundField(rounds=all_available_rounds)
    score = models.PositiveIntegerField()

    def __str__(self):
        return "Score submitted for %s - %s on %s at %s" % (
            self.submission.athlete_season,
            self.score,
            self.shot_round.name,
            self.event,
        )


class ContactResponse(models.Model):
    email = models.EmailField()
    agb_number = models.CharField(max_length=256)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)

    def __str__(self):
        return "Message from {} at {}".format(self.email, self.timestamp)
