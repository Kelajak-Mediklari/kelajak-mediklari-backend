from rest_framework import serializers

from apps.course.models import Course
from apps.course.serializers import SubjectSerializer


class CourseListSerializer(serializers.ModelSerializer):
    subject = SubjectSerializer()

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
        )
