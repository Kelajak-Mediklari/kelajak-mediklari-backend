from rest_framework import serializers

from apps.course.models import LessonPart, UserLessonPart
from apps.course.serializers import FileSerializer, GallerySerializer


class LessonPartDetailSerializer(serializers.ModelSerializer):
    galleries = GallerySerializer(many=True, read_only=True)
    attached_files = FileSerializer(many=True, read_only=True)
    is_user_lesson_part_completed = serializers.SerializerMethodField()
    user_lesson_id = serializers.SerializerMethodField()

    class Meta:
        model = LessonPart
        fields = (
            "id",
            "title",
            "content",
            "type",
            "video_url",
            "test",
            "galleries",
            "attached_files",
            "is_user_lesson_part_completed",
            "user_lesson_id",
        )

    def get_is_user_lesson_part_completed(self, obj):
        """Check if the current user has completed this lesson part"""
        request = self.context.get("request")
        if not request or not request.user or not request.user.is_authenticated:
            return False

        # Check if there's a completed UserLessonPart for this user and lesson part
        return UserLessonPart.objects.filter(
            lesson_part=obj,
            user_lesson__user_course__user=request.user,
            is_completed=True,
        ).exists()

    def get_user_lesson_id(self, obj):
        """Get the user lesson ID if exists, otherwise return None"""
        request = self.context.get("request")
        if not request or not request.user or not request.user.is_authenticated:
            return None

        # Find the UserLesson for this lesson part and user
        user_lesson_part = (
            UserLessonPart.objects.select_related("user_lesson")
            .filter(
                lesson_part=obj,
                user_lesson__user_course__user=request.user,
            )
            .first()
        )

        if user_lesson_part:
            return user_lesson_part.user_lesson.id
        return None
