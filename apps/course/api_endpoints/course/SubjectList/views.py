from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from apps.course.api_endpoints.course.SubjectList.serializers import (
    SubjectListSerializer,
)
from apps.course.models import Subject


class SubjectListAPIView(generics.ListAPIView):
    queryset = Subject.objects.filter(is_active=True)
    serializer_class = SubjectListSerializer
    permission_classes = (IsAuthenticated,)


__all__ = ["SubjectListAPIView"]
