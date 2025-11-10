from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated

from apps.course.api_endpoints.course.LessonPartDetail.serializers import (
    LessonPartDetailSerializer,
)
from apps.course.models import Lesson, LessonPart, UserCourse


class LessonPartDetailAPIView(generics.RetrieveAPIView):
    serializer_class = LessonPartDetailSerializer
    permission_classes = (IsAuthenticated,)
    lookup_field = "id"

    def get_object(self):
        lesson_part_id = self.kwargs.get(self.lookup_field)
        lesson_part = get_object_or_404(
            LessonPart.objects.select_related("lesson", "test").prefetch_related(
                "galleries", "attached_files"
            ),
            id=lesson_part_id,
            is_active=True,
        )

        # Check if user has access to this lesson part
        self._check_lesson_access(lesson_part)

        return lesson_part

    def _check_lesson_access(self, lesson_part):
        """Check if user has access to this lesson part"""
        user = self.request.user
        lesson = lesson_part.lesson
        course = lesson.course

        # Check if user has purchased the course (has UserCourse with is_free_trial=False)
        try:
            paid_user_course = UserCourse.objects.get(
                user=user, course=course, is_free_trial=False
            )
            # User has purchased the course, allow access to all lessons
            return
        except UserCourse.DoesNotExist:
            # User hasn't purchased the course, check if it's a free lesson
            pass

        # Get the first 3 lessons of the course ordered by order field
        first_three_lessons = list(
            Lesson.objects.filter(course=course, is_active=True).order_by("order")[:3]
        )

        # Check if current lesson is in the first 3
        if lesson in first_three_lessons:
            # This is a free lesson, allow access
            return
        else:
            # This is a paid lesson and user hasn't purchased the course
            raise PermissionDenied(
                "You need to purchase this course to access this lesson."
            )


__all__ = ["LessonPartDetailAPIView"]
