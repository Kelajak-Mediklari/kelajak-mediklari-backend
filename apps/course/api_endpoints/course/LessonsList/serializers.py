from rest_framework import serializers

from apps.course.models import Lesson, UserLesson


class LessonsListSerializer(serializers.ModelSerializer):
    # parts_count is now provided by the queryset annotation
    parts_count = serializers.IntegerField(read_only=True)
    is_user_lesson_created = serializers.SerializerMethodField()
    progress_percent = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = (
            "id",
            "title",
            "slug",
            "parts_count",
            "is_user_lesson_created",
            "progress_percent",
        )

    def get_is_user_lesson_created(self, obj):
        """Check if UserLesson exists for this lesson and the current user's course"""
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False

        # Use annotated field if available (from queryset optimization)
        if hasattr(obj, "has_user_lesson"):
            return obj.has_user_lesson

        # Fallback for when annotation is not available
        course_id = self.context.get("course_id")
        if not course_id:
            return False

        return UserLesson.objects.filter(
            lesson=obj, user_course__user=request.user, user_course__course_id=course_id
        ).exists()

    def get_progress_percent(self, obj):
        """Get progress percentage from UserLesson if it exists"""
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return 0.00

        # Use annotated field if available (from queryset optimization)
        if hasattr(obj, "user_progress_percent"):
            return float(obj.user_progress_percent)

        # Fallback for when annotation is not available
        course_id = self.context.get("course_id")
        if not course_id:
            return 0.00

        user_lesson = UserLesson.objects.filter(
            lesson=obj, user_course__user=request.user, user_course__course_id=course_id
        ).first()

        return float(user_lesson.progress_percent) if user_lesson else 0.00
