from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from apps.course.api_endpoints.course.SubmitAnswer.serializers import (
    SubmitAnswerSerializer,
)
from apps.course.models import UserAnswer, UserTest


class SubmitAnswerAPIView(generics.UpdateAPIView):
    serializer_class = SubmitAnswerSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        test_id = self.kwargs.get("test_id")
        answer_id = self.kwargs.get("answer_id")
        user = self.request.user

        # Get the active user test
        user_test = get_object_or_404(
            UserTest,
            test_id=test_id,
            user=user,
            is_in_progress=True,
            is_submitted=False,
        )

        # Get the user answer
        user_answer = get_object_or_404(UserAnswer, id=answer_id, user_test=user_test)

        return user_answer


__all__ = ["SubmitAnswerAPIView"]
