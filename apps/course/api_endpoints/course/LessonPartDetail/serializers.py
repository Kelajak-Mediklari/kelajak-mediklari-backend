from rest_framework import serializers

from apps.course.models import LessonPart
from apps.course.serializers import FileSerializer, GallerySerializer


class LessonPartDetailSerializer(serializers.ModelSerializer):
    galleries = GallerySerializer(many=True, read_only=True)
    attached_files = FileSerializer(many=True, read_only=True)

    class Meta:
        model = LessonPart
        fields = (
            "id",
            "title",
            "description",
            "type",
            "video_url",
            "test",
            "galleries",
            "attached_files",
        )
