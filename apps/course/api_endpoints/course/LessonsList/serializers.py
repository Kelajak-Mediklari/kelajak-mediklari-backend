from rest_framework import serializers

from apps.course.models import Lesson


class LessonsListSerializer(serializers.ModelSerializer):
    # parts_count is now provided by the queryset annotation
    parts_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Lesson
        fields = (
            "id",
            "title",
            "slug",
            "parts_count",
        )
