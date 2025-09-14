from django.shortcuts import get_object_or_404
from rest_framework import filters, generics
from rest_framework.permissions import IsAuthenticated

from apps.course.api_endpoints.course.LessonPartList.serializers import (
    LessonPartListSerializer,
)
from apps.course.models import Lesson, LessonPart


class LessonPartListAPIView(generics.ListAPIView):
    serializer_class = LessonPartListSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ("title", "description")
    lookup_field = "lesson_id"

    def get_queryset(self):
        lesson_id = self.kwargs.get(self.lookup_field)
        lesson = get_object_or_404(Lesson, id=lesson_id, is_active=True)

        return (
            LessonPart.objects.filter(lesson=lesson, is_active=True)
            .select_related("test")
            .prefetch_related("galleries", "attached_files")
            .order_by("order")
        )


__all__ = ["LessonPartListAPIView"]
