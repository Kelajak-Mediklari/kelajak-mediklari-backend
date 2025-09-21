from rest_framework import serializers

from apps.course.models import UserTest


class TestStartSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserTest
        fields = (
            "id",
            "start_date",
            "attempt_number",
            "is_in_progress",
        )
        read_only_fields = ("id", "start_date", "attempt_number", "is_in_progress")
