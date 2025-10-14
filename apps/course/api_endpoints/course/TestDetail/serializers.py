import random

from rest_framework import serializers

from apps.common.api_endpoints.common.file_serializers import AttachedFileSerializer
from apps.course.models import AnswerChoice, MatchingPair, Question, Test


class AnswerChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnswerChoice
        fields = (
            "id",
            "choice_text",
            "choice_image",
            "choice_label",
            "order",
        )


class MatchingLeftItemSerializer(serializers.ModelSerializer):
    """Serializer for matching question items (left side) - in order"""

    position = serializers.SerializerMethodField()

    class Meta:
        model = MatchingPair
        fields = (
            "position",
            "left_item",
        )

    def get_position(self, obj):
        # Use the order field as position (1-based indexing)
        return obj.order


class MatchingRightItemSerializer(serializers.ModelSerializer):
    """Serializer for matching answer items (right side) - will be shuffled"""

    position = serializers.SerializerMethodField()

    class Meta:
        model = MatchingPair
        fields = (
            "position",
            "right_item",
        )

    def get_position(self, obj):
        # Position will be set during shuffling process (new random position)
        return getattr(obj, "_shuffled_position", 1)


# True/False, Book Test, and Regular Test questions now use the Question model directly


class QuestionSerializer(serializers.ModelSerializer):
    matching_left_items = serializers.SerializerMethodField()
    matching_right_items = serializers.SerializerMethodField()
    choices = AnswerChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = (
            "id",
            "question_text",
            "instructions",
            "order",
            "correct_answer",  # For true/false questions
            "book_questions",  # For book test questions - JSON array
            "regular_question_type",  # For regular test questions
            "video_url",  # For regular test questions
            "question_image",  # For regular test questions
            "choices",  # For regular test questions
            "matching_left_items",
            "matching_right_items",
        )

    def get_matching_left_items(self, obj):
        """Get left items (questions) in order"""
        if hasattr(obj, "matching_pairs"):
            matching_pairs = obj.matching_pairs.all()
            return MatchingLeftItemSerializer(matching_pairs, many=True).data
        return []

    def get_matching_right_items(self, obj):
        """Get right items (answers) shuffled with new positions"""
        if hasattr(obj, "matching_pairs"):
            matching_pairs = list(obj.matching_pairs.all())
            # Shuffle the right items so user can't guess by order
            random.shuffle(matching_pairs)

            # Assign new shuffled positions (1-based indexing)
            for index, pair in enumerate(matching_pairs, 1):
                pair._shuffled_position = index

            return MatchingRightItemSerializer(matching_pairs, many=True).data
        return []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Get test type from context
        test_type = self.context.get("test_type")

        if test_type:
            # Remove fields based on test type
            fields_to_remove = []

            if test_type == "true_false":
                # For true/false questions, remove all other fields
                fields_to_remove.extend(
                    [
                        "order",
                        "instructions",
                        "correct_answer",
                        "book_questions",
                        "regular_question_type",
                        "video_url",
                        "question_image",
                        "choices",
                    ]
                )
            elif test_type == "book_test":
                # For book test questions, remove other type-specific fields
                fields_to_remove.extend(
                    [
                        "correct_answer",
                        "book_questions",
                        "regular_question_type",
                        "video_url",
                        "question_image",
                        "choices",
                    ]
                )
            elif test_type == "regular_test":
                # For regular test questions, remove other type-specific fields
                fields_to_remove.extend(["correct_answer", "book_questions"])
            else:
                # For all other test types, remove all type-specific fields
                fields_to_remove.extend(
                    [
                        "correct_answer",
                        "book_questions",
                        "regular_question_type",
                        "video_url",
                        "question_image",
                        "choices",
                    ]
                )

            if test_type != "matching":
                fields_to_remove.extend(["matching_left_items", "matching_right_items"])

            # Remove the fields from the serializer
            for field_name in fields_to_remove:
                self.fields.pop(field_name, None)


class TestDetailSerializer(serializers.ModelSerializer):
    attached_files = AttachedFileSerializer(many=True, read_only=True)
    is_submitted = serializers.SerializerMethodField()

    class Meta:
        model = Test
        fields = (
            "id",
            "title",
            "description",
            "type",
            "slug",
            "test_duration",
            "questions_count",
            "attached_files",
            "is_submitted",
        )

    def get_is_submitted(self, obj):
        """Check if the current user has submitted this test"""
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False

        # Import here to avoid circular imports
        from apps.course.models import UserTest

        # Check if user has any submitted test for this test
        return UserTest.objects.filter(
            test=obj, user=request.user, is_submitted=True
        ).exists()
