from rest_framework import serializers

from apps.course.models import AnswerChoice, Question, UserAnswer, UserTest


class AnswerChoiceResultSerializer(serializers.ModelSerializer):
    """Serializer for answer choices with result information"""

    is_user_selected = serializers.SerializerMethodField()

    class Meta:
        model = AnswerChoice
        fields = (
            "id",
            "choice_text",
            "choice_image",
            "choice_label",
            "is_correct",
            "is_user_selected",
            "order",
        )

    def get_is_user_selected(self, obj):
        """Check if this choice was selected by the user"""
        user_test = self.context.get("user_test")
        question = self.context.get("question")

        if not user_test or not question:
            return False

        try:
            user_answer = UserAnswer.objects.get(user_test=user_test, question=question)
            return (
                user_answer.selected_choice_id == obj.id
                if user_answer.selected_choice
                else False
            )
        except UserAnswer.DoesNotExist:
            return False


class QuestionResultSerializer(serializers.ModelSerializer):
    """Serializer for individual question results in user test"""

    user_answer_status = serializers.SerializerMethodField()
    choices = serializers.SerializerMethodField()
    question_type = serializers.CharField(
        source="regular_question_type", read_only=True
    )
    user_selected_choice_id = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = (
            "id",
            "question_text",
            "question_image",
            "video_url",
            "question_type",
            "user_answer_status",
            "choices",
            "user_selected_choice_id",
        )

    def get_user_answer_status(self, obj):
        """Get user's answer status for this question"""
        user_test = self.context.get("user_test")
        if not user_test:
            return "not_answered"

        try:
            user_answer = UserAnswer.objects.get(user_test=user_test, question=obj)
            return "correct" if user_answer.is_correct else "incorrect"
        except UserAnswer.DoesNotExist:
            return "not_answered"

    def get_choices(self, obj):
        """Get all answer choices with information about correctness and user selection"""
        choices = obj.choices.all().order_by("order")
        return AnswerChoiceResultSerializer(
            choices,
            many=True,
            context={
                "user_test": self.context.get("user_test"),
                "question": obj,
            },
        ).data

    def get_user_selected_choice_id(self, obj):
        """Get the ID of the choice selected by the user"""
        user_test = self.context.get("user_test")
        if not user_test:
            return None

        try:
            user_answer = UserAnswer.objects.get(user_test=user_test, question=obj)
            return (
                user_answer.selected_choice_id if user_answer.selected_choice else None
            )
        except UserAnswer.DoesNotExist:
            return None


class UserTestResultsSerializer(serializers.ModelSerializer):
    """Serializer for user test results with detailed information"""

    total_questions = serializers.SerializerMethodField()
    attempts_count = serializers.SerializerMethodField()
    award_coins = serializers.SerializerMethodField()
    award_points = serializers.SerializerMethodField()
    user_correct_answers = serializers.IntegerField(source="correct_answers")
    questions = serializers.SerializerMethodField()
    test_title = serializers.CharField(source="test.title", read_only=True)
    test_type = serializers.CharField(source="test.type", read_only=True)
    score_percentage = serializers.SerializerMethodField()

    class Meta:
        model = UserTest
        fields = (
            "id",
            "test_title",
            "test_type",
            "total_questions",
            "attempts_count",
            "award_coins",
            "award_points",
            "user_correct_answers",
            "score_percentage",
            "is_passed",
            "is_submitted",
            "start_date",
            "finish_date",
            "questions",
        )

    def get_total_questions(self, obj):
        """Get total number of questions in the test"""
        return obj.test.questions.filter(is_active=True).count()

    def get_attempts_count(self, obj):
        """Get total number of attempts by this user for this test"""
        return UserTest.objects.filter(user=obj.user, test=obj.test).count()

    def get_award_coins(self, obj):
        """Get coins awarded for this test (from related lesson part)"""
        # Find the lesson part that contains this test
        from apps.course.models import LessonPart

        lesson_part = LessonPart.objects.filter(test=obj.test, is_active=True).first()

        if lesson_part:
            return lesson_part.award_coin
        return 0

    def get_award_points(self, obj):
        """Get points awarded for this test (from related lesson part)"""
        # Find the lesson part that contains this test
        from apps.course.models import LessonPart

        lesson_part = LessonPart.objects.filter(test=obj.test, is_active=True).first()

        if lesson_part:
            return lesson_part.award_point
        return 0

    def get_score_percentage(self, obj):
        """Calculate score percentage"""
        if obj.total_questions == 0:
            return 0
        return round((obj.correct_answers / obj.total_questions) * 100, 2)

    def get_questions(self, obj):
        """Get all questions with user's answer status"""
        questions = obj.test.questions.filter(is_active=True).order_by("order")
        return QuestionResultSerializer(
            questions, many=True, context={"user_test": obj}
        ).data
