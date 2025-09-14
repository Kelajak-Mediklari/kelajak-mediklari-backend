from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from apps.course.api_endpoints.course.TestDetail.serializers import TestDetailSerializer
from apps.course.models import Test


class TestDetailAPIView(generics.RetrieveAPIView):
    serializer_class = TestDetailSerializer
    permission_classes = (IsAuthenticated,)
    lookup_field = "id"

    def get_object(self):
        test_id = self.kwargs.get(self.lookup_field)
        return get_object_or_404(
            Test.objects.filter(is_active=True),
            id=test_id,
        )


__all__ = ["TestDetailAPIView"]
