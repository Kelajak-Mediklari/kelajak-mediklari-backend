from rest_framework import serializers

from apps.course.models import LessonPart, UserLessonPart
from apps.course.serializers import FileSerializer, GallerySerializer


class LessonPartDetailSerializer(serializers.ModelSerializer):
    galleries = GallerySerializer(many=True, read_only=True)
    attached_files = FileSerializer(many=True, read_only=True)
    is_user_lesson_part_completed = serializers.SerializerMethodField()

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
