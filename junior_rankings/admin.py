from django.contrib import admin

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


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ["name", "date", "round_family"]
    list_filter = ["date", "round_family"]
    search_fields = ["name"]


admin.site.register(Season)
admin.site.register(Athlete)
admin.site.register(AthleteSeason)
admin.site.register(Score)
admin.site.register(Submission)
admin.site.register(SubmissionScore)
admin.site.register(ContactResponse)
