from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from apps.course.choices import LessonPartType
from apps.course.models import LessonPart, UserLesson, UserLessonPart


class UserLessonPartCreateSerializer(serializers.ModelSerializer):
    user_lesson_id = serializers.IntegerField(required=True)
    lesson_part_id = serializers.IntegerField(required=True)

    class Meta:
        model = UserLessonPart
        fields = [
            "id",
            "user_lesson_id",
            "lesson_part_id",
            "is_completed",
            "completion_date",
        ]
        read_only_fields = ["id", "is_completed", "completion_date"]

    def validate_user_lesson_id(self, value):
        """Validate that user_lesson exists and belongs to the current user"""
        request = self.context.get("request")
        if not request or not request.user:
            raise serializers.ValidationError("Authentication required.")

        try:
            user_lesson = UserLesson.objects.get(
                id=value, user_course__user=request.user
            )
            # Store user_lesson in context for later use
            self.context["user_lesson"] = user_lesson
        except UserLesson.DoesNotExist:
            raise serializers.ValidationError(
                "User lesson not found or does not belong to the current user."
            )
        return value

    def validate_lesson_part_id(self, value):
        """Validate that lesson_part exists and is active"""
        try:
            lesson_part = LessonPart.objects.get(id=value, is_active=True)
        except LessonPart.DoesNotExist:
            raise serializers.ValidationError("Lesson part not found or is not active.")
        return value

    def validate(self, attrs):
        """Cross-field validation"""
        user_lesson_id = attrs.get("user_lesson_id")
        lesson_part_id = attrs.get("lesson_part_id")
        request = self.context.get("request")

        if user_lesson_id and lesson_part_id:
            try:
                user_lesson = UserLesson.objects.get(id=user_lesson_id)
                lesson_part = LessonPart.objects.get(id=lesson_part_id)

                # Check if lesson_part belongs to the same lesson as user_lesson
                if lesson_part.lesson != user_lesson.lesson:
                    raise serializers.ValidationError(
                        "Lesson part does not belong to the same lesson as user lesson."
                    )

                # Prevent completion of test type lesson parts through this API
                if lesson_part.type == LessonPartType.TEST:
                    raise serializers.ValidationError(
                        "Test type lesson parts cannot be completed through this API. "
                        "Use the dedicated test completion API instead."
                    )

                # Check if this is a free trial and validate lesson access
                if user_lesson.user_course.is_free_trial:
                    # Get first 3 lessons of the course
                    first_three_lessons = list(
                        user_lesson.lesson.course.lessons.filter(
                            is_active=True
                        ).order_by("order")[:3]
                    )

                    if user_lesson.lesson not in first_three_lessons:
                        raise serializers.ValidationError(
                            "This lesson is not available for free trial. Please purchase the course to access it."
                        )

                # Check if UserLessonPart already exists
                if UserLessonPart.objects.filter(
                    user_lesson=user_lesson, lesson_part=lesson_part
                ).exists():
                    raise serializers.ValidationError(
                        "User lesson part already exists for this lesson part and user lesson."
                    )

            except (UserLesson.DoesNotExist, LessonPart.DoesNotExist):
                pass  # Individual field validation will catch these

        return attrs

    def create(self, validated_data):
        """Create UserLessonPart and mark it as completed"""
        user_lesson_id = validated_data.pop("user_lesson_id")
        lesson_part_id = validated_data.pop("lesson_part_id")

        user_lesson = UserLesson.objects.get(id=user_lesson_id)
        lesson_part = LessonPart.objects.get(id=lesson_part_id)

        try:
            user_lesson_part = UserLessonPart.objects.create(
                user_lesson=user_lesson, lesson_part=lesson_part, **validated_data
            )

            # Mark the lesson part as completed using the model's method
            user_lesson_part.mark_completed()

            return user_lesson_part
        except DjangoValidationError as e:
            raise serializers.ValidationError(str(e))
