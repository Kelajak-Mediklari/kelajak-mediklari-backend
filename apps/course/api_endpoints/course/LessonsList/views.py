from django.db.models import Count, Prefetch, Q
from django.shortcuts import get_object_or_404
from rest_framework import filters, generics
from rest_framework.permissions import IsAuthenticated

from apps.course.api_endpoints.course.LessonsList.serializers import (
    LessonsListSerializer,
)
from apps.course.models import Course, Lesson, UserCourse, UserLesson


class LessonsListAPIView(generics.ListAPIView):
    serializer_class = LessonsListSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ("title",)
    lookup_field = "course_id"

    def get_queryset(self):
        course_id = self.kwargs.get(self.lookup_field)
        course = get_object_or_404(Course, id=course_id, is_active=True)

        # Base queryset with parts count annotation
        queryset = Lesson.objects.filter(course=course, is_active=True).annotate(
            parts_count=Count("parts", filter=Q(parts__is_active=True))
        ).order_by("order")

        # Prefetch user lessons for the current user and course if authenticated
        if self.request.user.is_authenticated:
            user_lessons_prefetch = Prefetch(
                "user_lessons",
                queryset=UserLesson.objects.filter(
                    user_course__user=self.request.user,
                    user_course__course_id=course_id,
                ).select_related("user_course"),
                to_attr="filtered_user_lessons",
            )
            queryset = queryset.prefetch_related(user_lessons_prefetch)

        return queryset

    def get_serializer_context(self):
        """Add course_id and user_course to serializer context"""
        context = super().get_serializer_context()
        course_id = self.kwargs.get(self.lookup_field)
        context["course_id"] = course_id

        # Add user_course if user is authenticated and has access to the course
        if self.request.user.is_authenticated:
            try:
                user_course = UserCourse.objects.get(
                    user=self.request.user, course_id=course_id
                )
                context["user_course"] = user_course
            except UserCourse.DoesNotExist:
                context["user_course"] = None
        else:
            context["user_course"] = None

        return context


__all__ = ["LessonsListAPIView"]
