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

            # Mark related UserLessonPart as completed if test is passed
            if user_test.is_passed:
                lesson_part = LessonPart.objects.filter(
                    test=user_test.test, is_active=True
                ).first()

                if lesson_part:
                    user_lesson_part = UserLessonPart.objects.filter(
                        user_lesson__user_course__user=user, lesson_part=lesson_part
                    ).first()

                    if user_lesson_part and not user_lesson_part.is_completed:
                        user_lesson_part.mark_completed()

            serializer = self.get_serializer(user_test)
            return Response(serializer.data, status=status.HTTP_200_OK)


__all__ = ["FinishTestAPIView"]
