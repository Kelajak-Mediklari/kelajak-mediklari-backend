from rest_framework import serializers
from apps.payment.models import Transaction, PaymentProvider, PromoCode, UserPromoCode
from apps.course.models import Course


class TransactionCreateSerializer(serializers.ModelSerializer):
    provider_type = serializers.ChoiceField(
        choices=PaymentProvider.choices,
        source='provider',
        help_text="Payment provider type (Payme or Click)"
    )
    course_id = serializers.IntegerField(help_text="Course ID to purchase")
    duration = serializers.IntegerField(
        help_text="Duration in months",
        min_value=1,
        max_value=120
    )
    bypass_validation = serializers.BooleanField(
        required=False,
        default=False,
        help_text="Bypass amount validation (for discounted transactions)"
    )
    promo_code = serializers.CharField(
        max_length=255, 
        required=False, 
        allow_blank=True,
        help_text="Promo code used (optional)"
    )
    coins_used = serializers.IntegerField(
        required=False,
        min_value=0,
        help_text="Number of coins used (optional)"
    )

    class Meta:
        model = Transaction
        fields = ['amount', 'provider_type', 'course_id', 'duration', 'bypass_validation', 'promo_code', 'coins_used']

    def validate_amount(self, value):
        """Validate that amount is positive"""
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero")
        return value

    def validate(self, attrs):
        """Validate transaction amount and discounts"""
        course_id = attrs.get('course_id')
        amount = attrs.get('amount')
        bypass_validation = attrs.get('bypass_validation', False)
        promo_code = attrs.get('promo_code')
        coins_used = attrs.get('coins_used', 0)
        user = self.context['request'].user
        
        try:
            course = Course.objects.get(id=course_id, is_active=True)
        except Course.DoesNotExist:
            raise serializers.ValidationError({
                'course_id': 'Course not found, inactive, or deleted'
            })
        
        # Check if course has a price
        if course.price is None:
            raise serializers.ValidationError({
                'course_id': 'This course is free and does not require payment'
            })
        
        # Check if user already has this course
        from apps.course.models import UserCourse
        if UserCourse.objects.filter(user=user, course=course).exists():
            raise serializers.ValidationError({
                'course_id': 'You already have access to this course'
            })
        
        original_price = course.price  # Keep as Decimal
        
        # If bypass_validation is True, validate discounts and calculate expected amount
        if bypass_validation:
            expected_amount = original_price
            
            # Apply promo code discount if provided
            if promo_code:
                try:
                    promo_obj = PromoCode.objects.get(code=promo_code, is_active=True)
                    if not promo_obj.courses.filter(id=course_id).exists():
                        raise serializers.ValidationError({
                            'promo_code': 'This promo code is not valid for the selected course'
                        })
                    
                    # Check if user has already used this promo code
                    if UserPromoCode.objects.filter(
                        user=user, 
                        promocode=promo_obj, 
                        is_used=True
                    ).exists():
                        raise serializers.ValidationError({
                            'promo_code': 'You have already used this promo code'
                        })
                    
                    # Calculate promo discount (fixed amount, not percentage)
                    promo_discount = promo_obj.discount
                    expected_amount -= promo_discount
                    
                except PromoCode.DoesNotExist:
                    raise serializers.ValidationError({
                        'promo_code': 'Invalid or inactive promo code'
                    })
            
            # Apply coin discount if provided
            if coins_used:
                if coins_used > user.coin:
                    raise serializers.ValidationError({
                        'coins_used': f'You only have {user.coin} coins. Cannot use {coins_used} coins.'
                    })
                expected_amount -= coins_used
            
            # Ensure expected amount is not negative
            if expected_amount < 0:
                expected_amount = 0
            
            # Validate that the provided amount matches the calculated discounted amount
            from decimal import Decimal
            amount_decimal = Decimal(str(amount))
            expected_decimal = Decimal(str(expected_amount))
            
            if abs(amount_decimal - expected_decimal) > Decimal('0.01'):  # Allow small differences
                raise serializers.ValidationError({
                    'amount': f'Amount mismatch. Expected {expected_amount} (after discounts), but got {amount}. Please recalculate using the discount API.'
                })
            
            # Additional security: Validate promo code usage
            if promo_code:
                # Check if user has already used this promo code (double check)
                if UserPromoCode.objects.filter(
                    user=user, 
                    promocode__code=promo_code, 
                    is_used=True
                ).exists():
                    raise serializers.ValidationError({
                        'promo_code': 'This promo code has already been used by you'
                    })
            
            # Additional security: Validate coin balance
            if coins_used and coins_used > user.coin:
                raise serializers.ValidationError({
                    'coins_used': f'Insufficient coins. You have {user.coin} coins, cannot use {coins_used}'
                })
        
        else:
            # Standard validation - amount must match course price exactly
            from decimal import Decimal
            amount_decimal = Decimal(str(amount))
            original_decimal = Decimal(str(original_price))
            
            if amount_decimal != original_decimal:
                raise serializers.ValidationError({
                    'amount': f'Amount must be exactly {course.price} for this course. Current amount: {amount}. Use bypass_validation=True for discounted transactions.'
                })
        
        return attrs
