from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import UserLessonCreateSerializer


class UserLessonCreateAPIView(APIView):
    """
    Create a new UserLesson for a user.

    Requirements:
    - User must have a valid UserCourse (indicating they've paid for the course)
    - Lesson must exist and be active
    - Lesson must belong to the specified course
    - UserLesson must not already exist for this user-lesson combination
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = UserLessonCreateSerializer

    def post(self, request):
        """Create a new UserLesson"""
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )

        if serializer.is_valid():
            user_lesson = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


__all__ = ["UserLessonCreateAPIView"]
