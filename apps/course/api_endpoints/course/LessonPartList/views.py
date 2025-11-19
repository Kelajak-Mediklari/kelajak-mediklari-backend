from django.shortcuts import get_object_or_404
from rest_framework import filters, generics
from rest_framework.permissions import IsAuthenticated

from apps.course.api_endpoints.course.LessonPartList.serializers import (
    LessonPartListSerializer,
)
from apps.course.models import Lesson, LessonPart, UserLessonPart


class LessonPartListAPIView(generics.ListAPIView):
    serializer_class = LessonPartListSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ("title",)
    lookup_field = "lesson_id"

    def get_queryset(self):
        lesson_id = self.kwargs.get(self.lookup_field)
        lesson = get_object_or_404(Lesson, id=lesson_id, is_active=True)

        queryset = (
            LessonPart.objects.filter(lesson=lesson, is_active=True)
            .select_related("test")
            .prefetch_related("test__user_tests")
            .order_by("order")
        )

        # If user is authenticated, prefetch user progress data for efficient locking logic
        if self.request.user.is_authenticated:
            from django.db.models import Prefetch

            # Prefetch user lesson parts for this specific lesson and user
            user_lesson_parts_prefetch = Prefetch(
                "user_lesson_parts",
                queryset=UserLessonPart.objects.filter(
                    user_lesson__user_course__user=self.request.user,
                    user_lesson__lesson=lesson,
                ).select_related("user_lesson"),
                to_attr="filtered_user_lesson_parts",
            )

            queryset = queryset.prefetch_related(user_lesson_parts_prefetch)

        return queryset


__all__ = ["LessonPartListAPIView"]
