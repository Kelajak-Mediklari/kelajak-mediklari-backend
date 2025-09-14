from rest_framework import serializers

from apps.course.models import LessonPart


class LessonPartListSerializer(serializers.ModelSerializer):
    test_id = serializers.SerializerMethodField()

    class Meta:
        model = LessonPart
        fields = (
            "id",
            "title",
            "type",
            "order",
            "award_coin",
            "award_point",
            "test_id",
        )

    def get_test_id(self, obj):
        return obj.test.id if obj.test else None
