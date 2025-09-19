from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from apps.course.models import Lesson, UserCourse, UserLesson


class UserLessonCreateSerializer(serializers.ModelSerializer):
    user_course_id = serializers.IntegerField(required=True)
    lesson_id = serializers.IntegerField(required=True)

    class Meta:
        model = UserLesson
        fields = ["id", "user_course_id", "lesson_id"]
        read_only_fields = ["id"]

    def validate_user_course_id(self, value):
        """Validate that user_course exists and belongs to the current user"""
        request = self.context.get("request")
        if not request or not request.user:
            raise serializers.ValidationError("Authentication required.")

        try:
            user_course = UserCourse.objects.get(id=value, user=request.user)
        except UserCourse.DoesNotExist:
            raise serializers.ValidationError(
                "User course not found or user has not paid for this course."
            )
        return value

    def validate_lesson_id(self, value):
        """Validate that lesson exists and is active"""
        try:
            lesson = Lesson.objects.get(id=value, is_active=True)
        except Lesson.DoesNotExist:
            raise serializers.ValidationError("Lesson not found or is not active.")
        return value

    def validate(self, attrs):
        """Cross-field validation to ensure lesson belongs to the user's course"""
        user_course_id = attrs.get("user_course_id")
        lesson_id = attrs.get("lesson_id")

        if user_course_id and lesson_id:
            try:
                user_course = UserCourse.objects.get(id=user_course_id)
                lesson = Lesson.objects.get(id=lesson_id)

                # Check if lesson belongs to the same course as user_course
                if lesson.course != user_course.course:
                    raise serializers.ValidationError(
                        "Lesson does not belong to the specified course."
                    )

                # Check if UserLesson already exists
                if UserLesson.objects.filter(
                    user_course=user_course, lesson=lesson
                ).exists():
                    raise serializers.ValidationError(
                        "User lesson already exists for this lesson and course."
                    )

            except (UserCourse.DoesNotExist, Lesson.DoesNotExist):
                pass  # Individual field validation will catch these

        return attrs

    def create(self, validated_data):
        """Create UserLesson with proper relationships"""
        user_course_id = validated_data.pop("user_course_id")
        lesson_id = validated_data.pop("lesson_id")

        user_course = UserCourse.objects.get(id=user_course_id)
        lesson = Lesson.objects.get(id=lesson_id)

        try:
            user_lesson = UserLesson.objects.create(
                user_course=user_course, lesson=lesson, **validated_data
            )
            return user_lesson
        except DjangoValidationError as e:
            raise serializers.ValidationError(str(e))
