from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import UserLessonPartCreateSerializer


class UserLessonPartCreateAPIView(APIView):
    """
    Create a new UserLessonPart and mark it as completed.

    Requirements:
    - User must have a valid UserLesson (indicating they've started the lesson)
    - LessonPart must exist and be active
    - LessonPart must belong to the same lesson as UserLesson
    - LessonPart type must not be "test" (tests have separate completion API)
    - UserLessonPart must not already exist for this user-lesson-part combination
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = UserLessonPartCreateSerializer

    def post(self, request):
        """Create a new UserLessonPart and mark it as completed"""
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )

        if serializer.is_valid():
            user_lesson_part = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


__all__ = ["UserLessonPartCreateAPIView"]
