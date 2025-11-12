from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.course.api_endpoints.course.FinishTest.serializers import FinishTestSerializer
from apps.course.models import LessonPart, UserLessonPart, UserTest


class FinishTestAPIView(generics.UpdateAPIView):
    serializer_class = FinishTestSerializer
    permission_classes = (IsAuthenticated,)

    def update(self, request, *args, **kwargs):
        test_id = kwargs.get("test_id")
        user = request.user

        # Get the active user test
        user_test = get_object_or_404(
            UserTest,
            test_id=test_id,
            user=user,
            is_in_progress=True,
            is_submitted=False,
        )

        with transaction.atomic():
            # Check all answers and submit the test
            for user_answer in user_test.user_answers.all():
                user_answer.check_correctness()
                user_answer.save()

            # Submit the test (this will calculate scores)
            user_test.submit_test()

            # Find related lesson part
            lesson_part = LessonPart.objects.filter(
                test=user_test.test, is_active=True
            ).first()

            if lesson_part:
                user_lesson_part = UserLessonPart.objects.filter(
                    user_lesson__user_course__user=user, lesson_part=lesson_part
                ).first()

                if user_lesson_part and not user_lesson_part.is_completed:
                    # Always mark as completed and give partial awards on first attempt
                    if user_test.attempt_number == 1:
                        # Calculate percentage of correct answers
                        if user_test.total_questions > 0:
                            percentage = (
                                user_test.correct_answers / user_test.total_questions
                            )
                        else:
                            percentage = 0

                        # Calculate partial coins and points based on performance
                        partial_coins = int(lesson_part.award_coin * percentage)
                        partial_points = int(lesson_part.award_point * percentage)

                        # Mark as completed with partial awards
                        user_lesson_part.mark_completed_with_partial_awards(
                            coins=partial_coins, points=partial_points
                        )
                    else:
                        # Subsequent attempts: mark completed but no awards
                        user_lesson_part.mark_completed(give_awards=False)
                elif user_lesson_part and user_lesson_part.is_completed:
                    # User is retrying - no additional awards
                    pass

            serializer = self.get_serializer(user_test)
            return Response(serializer.data, status=status.HTTP_200_OK)


__all__ = ["FinishTestAPIView"]
