from rest_framework import serializers

from apps.course.models import UserCourse
from apps.course.serializers import CourseSerializer


class UserCoursesListSerializer(serializers.ModelSerializer):
    """Serializer for UserCourse model in list view"""

    course = CourseSerializer()

    class Meta:
        model = UserCourse
        fields = (
            "id",
            "course",
            "progress_percent",
            "is_completed",
            "start_date",
            "finish_date",
            "coins_earned",
            "points_earned",
        )
