from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from rest_framework import filters, generics
from rest_framework.permissions import IsAuthenticated

from apps.course.api_endpoints.course.LessonsList.serializers import (
    LessonsListSerializer,
)
from apps.course.models import Course, Lesson


class LessonsListAPIView(generics.ListAPIView):
    serializer_class = LessonsListSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ("title",)
    lookup_field = "course_id"

    def get_queryset(self):
        course_id = self.kwargs.get(self.lookup_field)
        course = get_object_or_404(Course, id=course_id, is_active=True)

        # Use annotation to count active parts at the database level
        return Lesson.objects.filter(course=course, is_active=True).annotate(
            parts_count=Count("parts", filter=Q(parts__is_active=True))
        )


__all__ = ["LessonsListAPIView"]
