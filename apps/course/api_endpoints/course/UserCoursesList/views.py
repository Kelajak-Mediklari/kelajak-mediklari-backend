from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics
from rest_framework.permissions import IsAuthenticated

from apps.course.api_endpoints.course.UserCoursesList.serializers import (
    UserCoursesListSerializer,
)
from apps.course.models import UserCourse


class UserCoursesListAPIView(generics.ListAPIView):
    """
    API endpoint for listing user's enrolled courses with progress tracking.
    """

    serializer_class = UserCoursesListSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    )
    filterset_fields = ("is_completed",)
    search_fields = ("course__title",)
    ordering_fields = ("progress_percent", "start_date", "finish_date")
    ordering = ("-start_date",)  # Default ordering by most recently started

    def get_queryset(self):
        return (
            UserCourse.objects.filter(user=self.request.user)
            .select_related("course", "course__subject")
            .prefetch_related("course__lessons")
        )


__all__ = ["UserCoursesListAPIView"]
