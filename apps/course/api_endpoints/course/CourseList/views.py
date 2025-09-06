from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics
from rest_framework.permissions import AllowAny

from apps.course.api_endpoints.course.CourseList.serializers import CourseListSerializer
from apps.course.models import Course


class CourseListAPIView(generics.ListAPIView):
    queryset = (
        Course.objects.filter(is_active=True)
        .select_related("subject")
        .prefetch_related("lessons")
    )
    serializer_class = CourseListSerializer
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_fields = ("subject", "is_main_course")
    search_fields = ("title",)


__all__ = ["CourseListAPIView"]
