from rest_framework import serializers

from apps.course.api_endpoints.course.TestDetail.serializers import QuestionSerializer
from apps.course.models import UserAnswer


class TestQuestionsSerializer(serializers.ModelSerializer):
    question_data = serializers.SerializerMethodField()
    test_type = serializers.SerializerMethodField()
    user_answer_id = serializers.SerializerMethodField()

    class Meta:
        model = UserAnswer
        fields = (
            "id",
            "question_data",
            "test_type",
            "user_answer_id",
        )

    def get_question_data(self, obj):
        """Return question with proper test type context"""
        context = self.context.copy()
        context["test_type"] = obj.user_test.test.type
        return QuestionSerializer(obj.question, context=context).data

    def get_test_type(self, obj):
        """Return the test type"""
        return obj.user_test.test.type

    def get_user_answer_id(self, obj):
        """Return the user answer ID for easy reference"""
        return obj.id
