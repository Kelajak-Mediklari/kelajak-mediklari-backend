from rest_framework import serializers

from apps.course.models import UserAnswer


class SubmitAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAnswer
        fields = (
            "id",
            "selected_choice",
            "boolean_answer",
            "text_answer",
            "matching_answer",
            "book_answer",
        )

    def validate_selected_choice(self, value):
        """Validate that selected choice belongs to the question"""
        if value and hasattr(self.instance, "question"):
            if value.question != self.instance.question:
                raise serializers.ValidationError(
                    "Selected choice must belong to the question"
                )
        return value

    def update(self, instance, validated_data):
        """Update user answer without checking correctness"""
        # Don't auto-check correctness during answer updates
        # We'll check all answers when test is submitted

        from django.utils import timezone

        # Update the fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Set answered_at timestamp when user actually provides an answer
        instance.answered_at = timezone.now()

        # Save without checking correctness
        instance.save(skip_correctness_check=True)

        return instance
