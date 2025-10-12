from rest_framework import serializers

from apps.course.models import LessonPart, UserTest


class LessonPartListSerializer(serializers.ModelSerializer):
    test_id = serializers.SerializerMethodField()
    test_type = serializers.SerializerMethodField()
    user_test_id = serializers.SerializerMethodField()

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
