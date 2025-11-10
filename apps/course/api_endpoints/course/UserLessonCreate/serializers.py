from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from apps.course.models import Lesson, UserCourse, UserLesson


class UserLessonCreateSerializer(serializers.ModelSerializer):
    user_course_id = serializers.IntegerField(required=False, allow_null=True)
    lesson_id = serializers.IntegerField(required=True)

    class Meta:
        model = UserLesson
        fields = ["id", "user_course_id", "lesson_id"]
        read_only_fields = ["id"]

    def validate_user_course_id(self, value):
        """Validate that user_course exists and belongs to the current user (if provided)"""
        if value is None:
            return value

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
        request = self.context.get("request")

        if lesson_id:
            try:
                lesson = Lesson.objects.get(id=lesson_id)

                # If user_course_id is not provided, check if lesson is in first 3 free lessons
                if not user_course_id:
                    # Get first 3 lessons of the course
                    first_three_lessons = Lesson.objects.filter(
                        course=lesson.course, is_active=True
                    ).order_by("order")[:3]

                    if lesson not in first_three_lessons:
                        raise serializers.ValidationError(
                            "This lesson is not available for free trial. Please purchase the course to access it."
                        )

                    # Check if free trial UserCourse already exists
                    existing_user_course = UserCourse.objects.filter(
                        user=request.user, course=lesson.course, is_free_trial=True
                    ).first()

                    if existing_user_course:
                        # Check if UserLesson already exists
                        if UserLesson.objects.filter(
                            user_course=existing_user_course, lesson=lesson
                        ).exists():
                            raise serializers.ValidationError(
                                "User lesson already exists for this lesson."
                            )
                else:
                    # If user_course_id is provided, validate as before
                    user_course = UserCourse.objects.get(id=user_course_id)

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
        user_course_id = validated_data.pop("user_course_id", None)
        lesson_id = validated_data.pop("lesson_id")
        request = self.context.get("request")

        lesson = Lesson.objects.get(id=lesson_id)

        try:
            # If no user_course_id provided, create or get free trial UserCourse
            if not user_course_id:
                user_course, created = UserCourse.objects.get_or_create(
                    user=request.user,
                    course=lesson.course,
                    is_free_trial=True,
                    defaults={"is_free_trial": True},
                )
            else:
                user_course = UserCourse.objects.get(id=user_course_id)

            user_lesson = UserLesson.objects.create(
                user_course=user_course, lesson=lesson, **validated_data
            )
            return user_lesson
        except DjangoValidationError as e:
            raise serializers.ValidationError(str(e))
