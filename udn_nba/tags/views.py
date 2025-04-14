from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiTypes,
    extend_schema,
    extend_schema_view,
)
from rest_framework import mixins, viewsets
from tags.models import Tag
from tags.serializers import TagDetailSerializer, TagSerializer


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                "name",
                OpenApiTypes.STR,
                description="Name of the tag to filter",
            ),
        ]
    )
)
class TagViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    """Viewset for tags."""

    queryset = Tag.objects.all()
    serializer_class = TagDetailSerializer
    lookup_field = "name"

    def get_queryset(self):
        """Retrieve tags."""

        name = self.request.query_params.get("name")
        queryset = self.queryset
        if name:
            queryset = queryset.filter(title__icontains=name)

        return queryset.distinct()

    def get_serializer_class(self):
        """Return the serializer class for request."""

        if self.action == "list":
            return TagSerializer

        return self.serializer_class
