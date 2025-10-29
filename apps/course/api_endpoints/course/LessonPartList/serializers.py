from rest_framework import serializers

from apps.course.models import LessonPart, UserLessonPart, UserTest


class LessonPartListSerializer(serializers.ModelSerializer):
    test_id = serializers.SerializerMethodField()
    test_type = serializers.SerializerMethodField()
    user_test_id = serializers.SerializerMethodField()
    is_locked = serializers.SerializerMethodField()

    class Meta:
        model = LessonPart
        fields = (
            "id",
            "title",
            "type",
            "order",
            "award_coin",
            "award_point",
            "test_id",
            "test_type",
            "user_test_id",
            "is_locked",
        )

    def get_test_id(self, obj):
        return obj.test.id if obj.test else None

    def get_test_type(self, obj):
        return obj.test.type if obj.test else None

    def get_user_test_id(self, obj):
        """Get the user's test attempt ID if they have taken this test"""
        if not obj.test:
            return None

        # Get the user from the request context
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return None

        # Get the most recent user test for this test
        user_test = (
            UserTest.objects.filter(user=request.user, test=obj.test)
            .order_by("-start_date")
            .first()
        )

        return user_test.id if user_test else None

    def get_is_locked(self, obj):
        """
        Determine if this lesson part is locked for the current user.
        Logic:
        - First lesson part (order=1) is always unlocked
        - Other lesson parts are locked until the previous lesson part is completed
        """
        # Get the user from the request context
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return True  # Lock for unauthenticated users

        # First lesson part is always unlocked
        if obj.order == 1:
            return False

        # Get the previous lesson part (by order)
        previous_part = (
            LessonPart.objects.filter(
                lesson=obj.lesson, is_active=True, order__lt=obj.order
            )
            .order_by("-order")
            .first()
        )

        if not previous_part:
            # If no previous part found, unlock this part
            return False

        # Check if user has completed the previous lesson part
        try:
            # First, check if user is enrolled in the course
            from apps.course.models import UserCourse, UserLesson

            user_course = UserCourse.objects.filter(
                user=request.user, course=obj.lesson.course
            ).first()

            if not user_course:
                # User hasn't enrolled in the course, so lock all parts except first
                return True

            # Try to use prefetched data if available
            if hasattr(obj, "filtered_user_lesson_parts"):
                # Use prefetched data
                user_lesson_parts = obj.filtered_user_lesson_parts
                previous_user_lesson_part = None

                for ulp in user_lesson_parts:
                    if ulp.lesson_part_id == previous_part.id:
                        previous_user_lesson_part = ulp
                        break

                # If previous part doesn't exist in user progress or isn't completed, lock this part
                if (
                    not previous_user_lesson_part
                    or not previous_user_lesson_part.is_completed
                ):
                    return True

                return False
            else:
                # Fallback to database queries if prefetch not available
                user_lesson, _ = UserLesson.objects.get_or_create(
                    user_course=user_course, lesson=obj.lesson
                )

                # Check if previous lesson part is completed
                previous_user_lesson_part = UserLessonPart.objects.filter(
                    user_lesson=user_lesson, lesson_part=previous_part
                ).first()

                # If previous part doesn't exist in user progress or isn't completed, lock this part
                if (
                    not previous_user_lesson_part
                    or not previous_user_lesson_part.is_completed
                ):
                    return True

                return False

        except Exception:
            # In case of any error, lock the lesson part for safety
            return True
