from rest_framework import serializers

from apps.course.models import UserCourse
from apps.course.serializers import CourseSerializer


class UserCoursesListSerializer(serializers.ModelSerializer):
    """Serializer for UserCourse model in list view"""

    course = CourseSerializer()
    completed_lessons_count = serializers.SerializerMethodField()

    class Meta:
        model = UserCourse
        fields = (
            "id",
            "course",
            "progress_percent",
            "is_completed",
            "start_date",
            "finish_date",
            "completed_lessons_count",
        )

    def get_completed_lessons_count(self, obj):
        """Get the count of completed lessons for this user course"""
        return obj.user_lessons.filter(is_completed=True).count()
