from django.db.models.functions import ExtractDay, ExtractMonth, ExtractYear
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, NumberFilter
from rest_framework import filters, status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination

from .models import Author, News, NewsSession
from .serializers import (
    AuthorSerializer,
    NewsDetailSerializer,
    NewsSerializer,
    NewsSessionSerializer,
)


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


class NewsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = News.objects.all()
    serializer_class = NewsDetailSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["tags", "author", "session"]
    search_fields = ["title"]
    ordering_fields = ["created_at"]
    ordering = ["-created_at"]

    pagination_class = PageNumberPagination
    pagination_class.page_query_param = "page"
    pagination_class.page_size_query_param = "size"
    pagination_class.page_size = 12
    pagination_class.max_page_size = 96

    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action == "list":
            return NewsSerializer
        return self.serializer_class
