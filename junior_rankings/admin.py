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

admin.site.register(Season)
admin.site.register(Athlete)
admin.site.register(AthleteSeason)
admin.site.register(Event)
admin.site.register(Score)
admin.site.register(Submission)
admin.site.register(SubmissionScore)
admin.site.register(ContactResponse)
