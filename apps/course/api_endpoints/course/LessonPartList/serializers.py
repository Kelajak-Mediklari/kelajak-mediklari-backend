from rest_framework import serializers

from apps.course.models import File, Gallery, LessonPart


class GallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Gallery
        fields = ("id", "image")


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ("id", "file")


class LessonPartListSerializer(serializers.ModelSerializer):
    galleries = GallerySerializer(many=True, read_only=True)
    attached_files = FileSerializer(many=True, read_only=True)
    test_id = serializers.SerializerMethodField()

    class Meta:
        model = LessonPart
        fields = (
            "id",
            "title",
            "description",
            "type",
            "order",
            "award_coin",
            "award_point",
            "video_url",
            "test_id",
            "galleries",
            "attached_files",
        )

    def get_test_id(self, obj):
        return obj.test.id if obj.test else None
