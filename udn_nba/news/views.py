from django.db.models.functions import ExtractDay, ExtractMonth, ExtractYear
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, NumberFilter
from rest_framework import filters, status, viewsets
from rest_framework.exceptions import ValidationError

from .models import Author, NewsSession
from .serializers import AuthorSerializer, NewsSessionSerializer


class AuthorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer


class NewsSessionDateFilter(FilterSet):
    year = NumberFilter(field_name="created_at", method="filter_year")
    month = NumberFilter(field_name="created_at", method="filter_month")
    day = NumberFilter(field_name="created_at", method="filter_day")

    class Meta:
        model = NewsSession
        fields = ["year", "month", "day"]

    def filter_queryset(self, queryset):
        """
        Override the filter_queryset method to validate filter dependencies
        before applying any filters.
        """
        params = self.request.query_params

        # Check for parameter dependencies
        if "month" in params and "year" not in params:
            raise ValidationError(
                {"month": "Year must be specified when filtering by month."}
            )

        if "day" in params and ("year" not in params or "month" not in params):
            raise ValidationError(
                {"day": "Both year and month must be specified when filtering by day."}
            )

        # If validation passes, apply the filters
        return super().filter_queryset(queryset)

    def filter_year(self, queryset, name, value):
        return queryset.annotate(year=ExtractYear("created_at")).filter(year=value)

    def filter_month(self, queryset, name, value):
        return queryset.annotate(month=ExtractMonth("created_at")).filter(month=value)

    def filter_day(self, queryset, name, value):
        return queryset.annotate(day=ExtractDay("created_at")).filter(day=value)


class NewsSessionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = NewsSession.objects.all()
    serializer_class = NewsSessionSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = NewsSessionDateFilter
