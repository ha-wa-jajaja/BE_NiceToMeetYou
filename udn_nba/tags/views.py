from django_filters.rest_framework import CharFilter, DjangoFilterBackend, FilterSet
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from tags.serializers import TagDetailSerializer, TagSerializer

from .models import Tag


class TagFilter(FilterSet):
    """Filter for Tag model."""

    name = CharFilter(field_name="name", lookup_expr="icontains")
    type = CharFilter(field_name="type", lookup_expr="exact")

    def filter_queryset(self, queryset):
        """Custom filtering to ensure only one filter is used at a time."""
        name = self.form.cleaned_data.get("name")
        tag_type = self.form.cleaned_data.get("type")

        if name and tag_type:
            raise ValidationError(
                {
                    "error": "Only one filter parameter (name or type) can be used at a time."
                }
            )

        return super().filter_queryset(queryset)

    class Meta:
        model = Tag
        fields = ["name", "type"]


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Viewset for tags."""

    queryset = Tag.objects.all()
    serializer_class = TagDetailSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = TagFilter

    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action == "list":
            return TagSerializer
        return self.serializer_class
