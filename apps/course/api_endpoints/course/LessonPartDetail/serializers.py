from rest_framework import serializers

from apps.common.api_endpoints.common.file_serializers import AttachedFileSerializer
from apps.course.models import LessonPart, UserLesson, UserLessonPart
from apps.course.serializers import GallerySerializer


class LessonPartDetailSerializer(serializers.ModelSerializer):
    galleries = GallerySerializer(many=True, read_only=True)
    attached_files = AttachedFileSerializer(many=True, read_only=True)
    is_user_lesson_part_completed = serializers.SerializerMethodField()
    user_lesson_id = serializers.SerializerMethodField()
    hls_video_url = serializers.SerializerMethodField()

    class Meta:
        model = LessonPart
        fields = (
            "id",
            "title",
            "content",
            "type",
            "hls_video_url",
            "hls_processing_status",
            "test",
            "galleries",
            "attached_files",
            "is_user_lesson_part_completed",
            "user_lesson_id",
        )

    def get_hls_video_url(self, obj):
        """
        Return the full HLS video URL if conversion is completed,
        otherwise return None
        """
        if obj.hls_processing_status == "completed" and obj.hls_video_url:
            request = self.context.get("request")
            if request:
                # Return absolute URL
                return request.build_absolute_uri(obj.hls_video_url)
            return obj.hls_video_url
        return None

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

        # First, try to find UserLesson through UserLessonPart
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

        # If no UserLessonPart exists, try to find UserLesson directly
        # This handles cases where user started a lesson but hasn't created UserLessonPart yet
        user_lesson = UserLesson.objects.filter(
            lesson=obj.lesson,
            user_course__user=request.user,
        ).first()

        if user_lesson:
            return user_lesson.id

        return None
