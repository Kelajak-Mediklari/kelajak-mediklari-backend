from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from apps.course.api_endpoints.course.TestQuestions.serializers import (
    TestQuestionsSerializer,
)
from apps.course.models import AnswerChoice, MatchingPair, UserAnswer, UserTest


class TestQuestionsAPIView(generics.ListAPIView):
    serializer_class = TestQuestionsSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        test_id = self.kwargs.get("test_id")
        user = self.request.user

        # Get the active user test
        user_test = get_object_or_404(
            UserTest,
            test_id=test_id,
            user=user,
            is_in_progress=True,
            is_submitted=False,
        )

        # Get the test type for optimization
        test_type = user_test.test.type

        # Build optimized queryset based on test type
        queryset = UserAnswer.objects.filter(user_test=user_test)

        if test_type == "matching":
            queryset = queryset.select_related(
                "question", "question__test"
            ).prefetch_related(
                Prefetch(
                    "question__matching_pairs",
                    queryset=MatchingPair.objects.order_by("order"),
                )
            )
        elif test_type == "regular_test":
            queryset = queryset.select_related(
                "question", "question__test"
            ).prefetch_related(
                Prefetch(
                    "question__choices", queryset=AnswerChoice.objects.order_by("order")
                )
            )
        else:
            queryset = queryset.select_related("question", "question__test")

        return queryset.order_by("question__order")


__all__ = ["TestQuestionsAPIView"]
