from rest_framework import serializers

from apps.course.models import Course, Gallery, Subject


class GallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Gallery
        fields = ("id", "image")


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
            "video_preview",
            "subject",
            "learning_outcomes",
            "duration",
            "duration_months",
            "price",
            "is_unlimited",
            "is_main_course",
            "is_can_pay_with_coin",
            "is_can_pay_with_referral",
            "lessons_count",
        )

    def get_lessons_count(self, obj):
        return obj.lessons.filter(is_active=True).count()
