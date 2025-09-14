from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from apps.course.api_endpoints.course.LessonPartDetail.serializers import (
    LessonPartDetailSerializer,
)
from apps.course.models import LessonPart


class LessonPartDetailAPIView(generics.RetrieveAPIView):
    serializer_class = LessonPartDetailSerializer
    permission_classes = (IsAuthenticated,)
    lookup_field = "id"

    def get_object(self):
        lesson_part_id = self.kwargs.get(self.lookup_field)
        return get_object_or_404(
            LessonPart.objects.select_related("lesson", "test").prefetch_related(
                "galleries", "attached_files"
            ),
            id=lesson_part_id,
            is_active=True,
        )


__all__ = ["LessonPartDetailAPIView"]
