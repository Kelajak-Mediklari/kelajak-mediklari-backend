from rest_framework import serializers

from apps.course.models import Course
from apps.course.serializers import SubjectSerializer


class CourseListSerializer(serializers.ModelSerializer):
    subject = SubjectSerializer()
    lessons_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = (
            "id",
            "title",
            "slug",
            "description",
            "cover",
            "subject",
            "learning_outcomes",
            "duration",
            "is_main_course",
            "lessons_count",
        )

    def get_lessons_count(self, obj):
        return obj.lessons.filter(is_active=True).count()
