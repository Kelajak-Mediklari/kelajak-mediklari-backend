from rest_framework import serializers

from apps.course.models import UserTest


class FinishTestSerializer(serializers.ModelSerializer):
    score_percent = serializers.SerializerMethodField()

    class Meta:
        model = UserTest
        fields = (
            "id",
            "is_passed",
            "is_submitted",
            "total_questions",
            "correct_answers",
            "score_percent",
            "finish_date",
        )
        read_only_fields = fields

    def get_score_percent(self, obj):
        if obj.total_questions == 0:
            return 0
        return round((obj.correct_answers / obj.total_questions) * 100, 2)
