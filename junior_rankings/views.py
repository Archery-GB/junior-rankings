import itertools

from django.db.models import Count
from django.views.generic import DetailView, ListView, TemplateView
from django.utils import timezone


class Root(TemplateView):
    template_name = "junior_rankings/root.html"

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            page_name="root", **kwargs
        )
