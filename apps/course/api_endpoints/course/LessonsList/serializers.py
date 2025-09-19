from rest_framework import serializers

from apps.course.models import Lesson, UserLesson


class LessonsListSerializer(serializers.ModelSerializer):
    # parts_count is now provided by the queryset annotation
    parts_count = serializers.IntegerField(read_only=True)
    is_user_lesson_created = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = (
            "id",
            "title",
            "slug",
            "parts_count",
            "is_user_lesson_created",
        )

    def get_is_user_lesson_created(self, obj):
        """Check if UserLesson exists for this lesson and the current user's course"""
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False

        # Get the course_id from the view context
        course_id = self.context.get("course_id")
        if not course_id:
            return False

        # Check if UserLesson exists for this lesson and user's course
        return UserLesson.objects.filter(
            lesson=obj, user_course__user=request.user, user_course__course_id=course_id
        ).exists()
