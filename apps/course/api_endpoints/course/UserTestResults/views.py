from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from apps.course.api_endpoints.course.UserTestResults.serializers import (
    UserTestResultsSerializer,
)
from apps.course.models import UserTest


class UserTestResultsAPIView(generics.RetrieveAPIView):
    """
    API view to retrieve user test results with detailed information
    including questions and user's answer status
    """

    serializer_class = UserTestResultsSerializer
    permission_classes = (IsAuthenticated,)
    lookup_field = "user_test_id"

    def get_object(self):
        user_test_id = self.kwargs.get(self.lookup_field)
        user = self.request.user

        # Get the user test, ensuring it belongs to the authenticated user
        return get_object_or_404(
            UserTest.objects.select_related("test", "user").prefetch_related(
                "test__questions__test", "user_answers__question__test"
            ),
            id=user_test_id,
            user=user,
        )


__all__ = ["UserTestResultsAPIView"]
