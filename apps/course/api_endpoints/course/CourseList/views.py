from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics
from rest_framework.permissions import AllowAny

from apps.course.api_endpoints.course.CourseList.serializers import CourseListSerializer
from apps.course.models import Course, UserCourse


class CourseListAPIView(generics.ListAPIView):
    serializer_class = CourseListSerializer
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_fields = ("is_main_course",)
    search_fields = ("title",)

    def get_queryset(self):
        subject_id = self.kwargs.get("subject_id")
        queryset = Course.objects.filter(is_active=True, subject_id=subject_id)

        # Exclude courses that the user is already enrolled in
        if self.request.user.is_authenticated:
            user_course_ids = UserCourse.objects.filter(
                user=self.request.user
            ).values_list("course_id", flat=True)
            queryset = queryset.exclude(id__in=user_course_ids)

        return queryset.select_related("subject").prefetch_related("lessons")


__all__ = ["CourseListAPIView"]
