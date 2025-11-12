from rest_framework import serializers

from apps.course.models import UserCourse
from apps.course.serializers import CourseSerializer
from apps.users.models import GroupMember


class UserCoursesListSerializer(serializers.ModelSerializer):
    """Serializer for UserCourse model in list view"""

    course = CourseSerializer()
    completed_lessons_count = serializers.SerializerMethodField()
    is_group_member = serializers.SerializerMethodField()

    class Meta:
        model = UserCourse
        fields = (
            "id",
            "course",
            "progress_percent",
            "is_completed",
            "start_date",
            "finish_date",
            "is_expired",
            "is_free_trial",
            "completed_lessons_count",
            "is_group_member",
        )

    def get_completed_lessons_count(self, obj):
        """Get the count of completed lessons for this user course"""
        return obj.user_lessons.filter(is_completed=True).count()

    def get_is_group_member(self, obj):
        """Check if the user is a group member"""
        return GroupMember.objects.filter(
            user=self.context["request"].user, group__course=obj.course, is_active=True
        ).exists()
