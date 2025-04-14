from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiTypes,
    extend_schema,
    extend_schema_view,
)
from rest_framework import mixins, viewsets
from rest_framework.exceptions import ValidationError
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
            OpenApiParameter(
                "type",
                OpenApiTypes.STR,
                description="Type of the tag to filter",
            ),
        ],
    ),
)
class TagViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    """Viewset for tags."""

    queryset = Tag.objects.all()
    serializer_class = TagDetailSerializer

    def get_queryset(self):
        """Retrieve tags."""

        name = self.request.query_params.get("name")
        tag_type = self.request.query_params.get("type")
        queryset = self.queryset

        #  Check if both filters are provided
        if name and tag_type:
            raise ValidationError(
                {
                    "error": "Only one filter parameter (name or type) can be used at a time."
                }
            )

        if name:
            queryset = queryset.filter(name__icontains=name)
        elif tag_type:
            queryset = queryset.filter(type=tag_type)

        return queryset.distinct()

    def get_serializer_class(self):
        """Return the serializer class for request."""

        if self.action == "list":
            return TagSerializer

        return self.serializer_class
