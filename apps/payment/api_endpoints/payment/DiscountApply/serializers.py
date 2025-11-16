from rest_framework import serializers

from apps.course.models import Course
from apps.payment.models import PromoCode


class DiscountApplySerializer(serializers.Serializer):
    course_id = serializers.IntegerField(help_text="Course ID to apply discounts to")
    promo_code = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
        help_text="Promo code to apply (optional)",
    )
    coins_to_use = serializers.IntegerField(
        required=False, min_value=0, help_text="Number of coins to use (optional)"
    )

    def validate_course_id(self, value):
        """Validate that course exists and is active"""
        try:
            course = Course.objects.get(id=value, is_active=True)
            if course.price is None:
                raise serializers.ValidationError(
                    "This course is free and cannot use discounts"
                )
            return value
        except Course.DoesNotExist:
            raise serializers.ValidationError("Course not found or inactive")

    def validate_promo_code(self, value):
        """Validate that promo code exists and is active (if provided)"""
        if not value:
            return value

        try:
            promo_code = PromoCode.objects.get(code=value, is_active=True)
            return value
        except PromoCode.DoesNotExist:
            raise serializers.ValidationError("Invalid or inactive promo code")

    def validate_coins_to_use(self, value):
        """Validate coins amount"""
        if value is not None and value < 0:
            raise serializers.ValidationError("Coins amount cannot be negative")
        return value

    def validate(self, attrs):
        """Validate promo code for course and user coin balance"""
        course_id = attrs.get("course_id")
        promo_code = attrs.get("promo_code")
        coins_to_use = attrs.get("coins_to_use", 0)

        try:
            course = Course.objects.get(id=course_id, is_active=True)
        except Course.DoesNotExist:
            raise serializers.ValidationError(
                {"course_id": "Course not found, inactive, or deleted"}
            )

        user = self.context["request"].user

        # Check if user already has this course (excluding free trial)
        from apps.course.models import UserCourse

        if UserCourse.objects.filter(
            user=user, course=course, is_free_trial=False
        ).exists():
            raise serializers.ValidationError(
                {"course_id": "You already have access to this course"}
            )

        # Validate promo code for this course
        if promo_code:
            promo_obj = PromoCode.objects.get(code=promo_code)
            if not promo_obj.courses.filter(id=course_id).exists():
                raise serializers.ValidationError(
                    {
                        "promo_code": "This promo code is not valid for the selected course"
                    }
                )

        # Validate user has enough coins
        if coins_to_use and coins_to_use > user.coin:
            raise serializers.ValidationError(
                {
                    "coins_to_use": f"You only have {user.coin} coins. Cannot use {coins_to_use} coins."
                }
            )

        return attrs
