from rest_framework import serializers

from apps.course.models import (
    AnswerChoice,
    MatchingPair,
    Question,
    UserAnswer,
    UserTest,
)


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


class MatchingPairResultSerializer(serializers.ModelSerializer):
    """Serializer for matching pairs with result information"""

    user_matched_right_item = serializers.SerializerMethodField()
    is_correct_match = serializers.SerializerMethodField()

    class Meta:
        model = MatchingPair
        fields = (
            "id",
            "left_item",
            "right_item",
            "user_matched_right_item",
            "is_correct_match",
            "order",
        )

    def get_user_matched_right_item(self, obj):
        """Get the right item that user matched with this left item"""
        user_test = self.context.get("user_test")
        question = self.context.get("question")

        if not user_test or not question:
            return None

        try:
            user_answer = UserAnswer.objects.get(user_test=user_test, question=question)
            if user_answer.matching_answer:
                # matching_answer is a dict like {left_item: right_item}
                return user_answer.matching_answer.get(obj.left_item)
            return None
        except UserAnswer.DoesNotExist:
            return None

    def get_is_correct_match(self, obj):
        """Check if user's match for this pair is correct"""
        user_test = self.context.get("user_test")
        question = self.context.get("question")

        if not user_test or not question:
            return False

        try:
            user_answer = UserAnswer.objects.get(user_test=user_test, question=question)
            if user_answer.matching_answer:
                user_matched = user_answer.matching_answer.get(obj.left_item)
                return user_matched == obj.right_item
            return False
        except UserAnswer.DoesNotExist:
            return False


class BookQuestionResultSerializer(serializers.Serializer):
    """Serializer for individual book test question results"""

    question_number = serializers.IntegerField()
    expected_answer = serializers.CharField()
    user_answer = serializers.CharField(allow_null=True)
    is_correct = serializers.BooleanField()


class QuestionResultSerializer(serializers.ModelSerializer):
    """Serializer for individual question results in user test"""

    user_answer_status = serializers.SerializerMethodField()
    choices = serializers.SerializerMethodField()
    question_type = serializers.SerializerMethodField()
    user_selected_choice_id = serializers.SerializerMethodField()

    # For matching tests
    matching_pairs = serializers.SerializerMethodField()
    user_matching_answer = serializers.SerializerMethodField()

    # For book tests
    book_questions_data = serializers.SerializerMethodField()

    # For true/false tests
    correct_answer = serializers.BooleanField(read_only=True)
    user_boolean_answer = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = (
            "id",
            "question_text",
            "question_image",
            "video_url",
            "instructions",
            "question_type",
            "user_answer_status",
            "choices",
            "user_selected_choice_id",
            "matching_pairs",
            "user_matching_answer",
            "book_questions_data",
            "correct_answer",
            "user_boolean_answer",
        )

    def get_question_type(self, obj):
        """Get the question type based on test type"""
        test_type = obj.test.type
        if test_type == "regular_test":
            return obj.regular_question_type
        return test_type

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
        """Get all answer choices with information about correctness and user selection (for regular tests)"""
        if obj.test.type != "regular_test":
            return None

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
        """Get the ID of the choice selected by the user (for regular tests)"""
        if obj.test.type != "regular_test":
            return None

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

    def get_matching_pairs(self, obj):
        """Get all matching pairs with user's answers (for matching tests)"""
        if obj.test.type != "matching":
            return None

        pairs = obj.matching_pairs.all().order_by("order")
        return MatchingPairResultSerializer(
            pairs,
            many=True,
            context={
                "user_test": self.context.get("user_test"),
                "question": obj,
            },
        ).data

    def get_user_matching_answer(self, obj):
        """Get user's matching answer as a dictionary (for matching tests)"""
        if obj.test.type != "matching":
            return None

        user_test = self.context.get("user_test")
        if not user_test:
            return None

        try:
            user_answer = UserAnswer.objects.get(user_test=user_test, question=obj)
            return user_answer.matching_answer
        except UserAnswer.DoesNotExist:
            return None

    def get_book_questions_data(self, obj):
        """Get book test questions with user's answers (for book tests)"""
        if obj.test.type != "book_test":
            return None

        user_test = self.context.get("user_test")
        if not obj.book_questions:
            return None

        # Get user's answers
        user_answers = []
        try:
            user_answer = UserAnswer.objects.get(user_test=user_test, question=obj)
            user_answers = user_answer.book_answer if user_answer.book_answer else []
        except UserAnswer.DoesNotExist:
            pass

        # Parse book questions structure
        book_questions_list = []
        if isinstance(obj.book_questions, list) and len(obj.book_questions) > 0:
            book_data = obj.book_questions[0]
            if isinstance(book_data, dict) and "questions" in book_data:
                questions_list = book_data["questions"]

                for i, book_question in enumerate(questions_list):
                    question_number = book_question.get("question_number", i + 1)
                    expected_answer = book_question.get("expected_answer", "")
                    user_answer_value = (
                        user_answers[i] if i < len(user_answers) else None
                    )
                    is_correct = (
                        user_answer_value == expected_answer
                        if user_answer_value
                        else False
                    )

                    book_questions_list.append(
                        {
                            "question_number": question_number,
                            "expected_answer": expected_answer,
                            "user_answer": user_answer_value,
                            "is_correct": is_correct,
                        }
                    )
            else:
                # Fallback for old structure
                for i, book_question in enumerate(obj.book_questions):
                    question_number = book_question.get("question_number", i + 1)
                    expected_answer = book_question.get("expected_answer", "")
                    user_answer_value = (
                        user_answers[i] if i < len(user_answers) else None
                    )
                    is_correct = (
                        user_answer_value == expected_answer
                        if user_answer_value
                        else False
                    )

                    book_questions_list.append(
                        {
                            "question_number": question_number,
                            "expected_answer": expected_answer,
                            "user_answer": user_answer_value,
                            "is_correct": is_correct,
                        }
                    )

        return book_questions_list

    def get_user_boolean_answer(self, obj):
        """Get user's boolean answer (for true/false tests)"""
        if obj.test.type != "true_false":
            return None

        user_test = self.context.get("user_test")
        if not user_test:
            return None

        try:
            user_answer = UserAnswer.objects.get(user_test=user_test, question=obj)
            return user_answer.boolean_answer
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
