from rest_framework import serializers

from apps.course.models import Course, File, Gallery, Subject


class GallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Gallery
        fields = ("id", "image")


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ("id", "file")


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ("id", "title", "slug", "icon")


class CourseSerializer(serializers.ModelSerializer):
    """Global serializer for Course model that can be reused across different APIs"""

    lessons_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = (
            "id",
            "title",
            "slug",
            "cover",
            "subject",
            "learning_outcomes",
            "duration",
            "is_main_course",
            "lessons_count",
        )

    def get_lessons_count(self, obj):
        return obj.lessons.filter(is_active=True).count()
