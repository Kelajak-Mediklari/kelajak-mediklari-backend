import random

from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.course.api_endpoints.course.TestStart.serializers import TestStartSerializer
from apps.course.models import (
    LessonPart,
    Question,
    Test,
    UserAnswer,
    UserCourse,
    UserLesson,
    UserLessonPart,
    UserTest,
)


class TestStartAPIView(generics.CreateAPIView):
    serializer_class = TestStartSerializer
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        test_id = kwargs.get("test_id")
        user = request.user

        # Get the test
        test = get_object_or_404(Test, id=test_id, is_active=True)

        with transaction.atomic():
            # Check if user has an active test session for this test
            existing_test = UserTest.objects.filter(
                user=user, test=test, is_in_progress=True, is_submitted=False
            ).first()

            if existing_test:
                # Return existing test session
                serializer = self.get_serializer(existing_test)
                return Response(serializer.data, status=status.HTTP_200_OK)

            # Get the next attempt number
            last_attempt = (
                UserTest.objects.filter(user=user, test=test)
                .order_by("-attempt_number")
                .first()
            )

            attempt_number = 1 if not last_attempt else last_attempt.attempt_number + 1

            # Create new UserTest
            user_test = UserTest.objects.create(
                user=user,
                test=test,
                attempt_number=attempt_number,
                is_in_progress=True,
                is_submitted=False,
            )

            # Find related lesson part and create/update UserLessonPart
            lesson_part = LessonPart.objects.filter(test=test, is_active=True).first()
            if lesson_part:
                from apps.course.models import Lesson

                # Check if this lesson is in the first 3 free lessons
                first_three_lessons = list(
                    Lesson.objects.filter(
                        course=lesson_part.lesson.course, is_active=True
                    ).order_by("order")[:3]
                )

                is_free_lesson = lesson_part.lesson in first_three_lessons

                # Get or create UserCourse
                # First try to get a paid UserCourse
                user_course = UserCourse.objects.filter(
                    user=user, course=lesson_part.lesson.course, is_free_trial=False
                ).first()

                if not user_course:
                    # User hasn't paid, check if it's a free lesson
                    if is_free_lesson:
                        # Create or get free trial UserCourse
                        user_course, created = UserCourse.objects.get_or_create(
                            user=user,
                            course=lesson_part.lesson.course,
                            is_free_trial=True,
                            defaults={"is_free_trial": True},
                        )
                    else:
                        # Not a free lesson and user hasn't paid
                        # This shouldn't happen if access control is working properly
                        # But we'll create a paid UserCourse anyway (maybe payment was processed elsewhere)
                        user_course, created = UserCourse.objects.get_or_create(
                            user=user,
                            course=lesson_part.lesson.course,
                            defaults={"is_free_trial": False},
                        )

                # Get or create UserLesson
                user_lesson, created = UserLesson.objects.get_or_create(
                    user_course=user_course, lesson=lesson_part.lesson
                )

                # Get or create UserLessonPart and mark as in progress
                user_lesson_part, created = UserLessonPart.objects.get_or_create(
                    user_lesson=user_lesson, lesson_part=lesson_part
                )
                # Don't mark as completed yet - will be done in finish test API

            # Generate random questions for the test
            self._generate_user_answers(user_test, test)

            serializer = self.get_serializer(user_test)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    def _generate_user_answers(self, user_test, test):
        """Generate UserAnswer objects with random questions for the test"""
        # Get all questions for this test
        all_questions = Question.objects.filter(test=test, is_active=True).order_by(
            "order"
        )

        questions_count = test.questions_count
        total_available = all_questions.count()

        # If we have fewer questions than requested, use all available
        if total_available <= questions_count:
            selected_questions = list(all_questions)
        else:
            # Randomly select questions
            selected_questions = random.sample(list(all_questions), questions_count)

        # Create UserAnswer objects for selected questions
        user_answers = []
        for question in selected_questions:
            user_answer = UserAnswer(
                user_test=user_test,
                question=question,
                # Don't set any answers yet - just create empty answer objects
                is_correct=False,
            )
            user_answers.append(user_answer)

        # Bulk create all user answers
        UserAnswer.objects.bulk_create(user_answers)


__all__ = ["TestStartAPIView"]
