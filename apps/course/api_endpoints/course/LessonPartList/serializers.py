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
        # First lesson part is always unlocked
        if obj.order == 1:
            return False

        # Get the user from the request context
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return True

        # Get the previous lesson part (by order)
        previous_part = (
            LessonPart.objects.filter(
                lesson=obj.lesson, is_active=True, order__lt=obj.order
            )
            .order_by("-order")
            .first()
        )

        if not previous_part:
            return False

        # Check if user has completed the previous lesson part
        previous_user_lesson_part = UserLessonPart.objects.filter(
            user_lesson__user_course__user=request.user,
            user_lesson__lesson=obj.lesson,
            lesson_part=previous_part,
            is_completed=True,
        ).exists()

        # If previous part is completed, unlock this part (return False)
        # If previous part is not completed, lock this part (return True)
        return not previous_user_lesson_part
