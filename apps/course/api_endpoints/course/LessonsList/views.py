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
        queryset = Lesson.objects.filter(course=course, is_active=True).annotate(
            parts_count=Count("parts", filter=Q(parts__is_active=True))
        )

        # Add user progress annotation if user is authenticated
        if self.request.user.is_authenticated:
            from django.db.models import (
                BooleanField,
                Case,
                DecimalField,
                IntegerField,
                When,
            )

            queryset = queryset.annotate(
                user_progress_percent=Case(
                    When(
                        user_lessons__user_course__user=self.request.user,
                        user_lessons__user_course__course_id=course_id,
                        then="user_lessons__progress_percent",
                    ),
                    default=0.00,
                    output_field=DecimalField(max_digits=5, decimal_places=2),
                ),
                has_user_lesson=Case(
                    When(
                        user_lessons__user_course__user=self.request.user,
                        user_lessons__user_course__course_id=course_id,
                        then=True,
                    ),
                    default=False,
                    output_field=BooleanField(),
                ),
                user_lesson_id_annotation=Case(
                    When(
                        user_lessons__user_course__user=self.request.user,
                        user_lessons__user_course__course_id=course_id,
                        then="user_lessons__id",
                    ),
                    default=None,
                    output_field=IntegerField(),
                ),
            )

        return queryset

    def get_serializer_context(self):
        """Add course_id to serializer context"""
        context = super().get_serializer_context()
        context["course_id"] = self.kwargs.get(self.lookup_field)
        return context


__all__ = ["LessonsListAPIView"]
