from rest_framework import serializers

from apps.course.models import Lesson


class LessonsListSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source="course.title", read_only=True)
    parts_count = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = (
            "id",
            "title",
            "slug",
            "course_title",
            "parts_count",
        )

    def get_parts_count(self, obj):
        return obj.parts.filter(is_active=True).count()
