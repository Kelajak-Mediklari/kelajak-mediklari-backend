from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import transaction

from apps.course.models import Course
from apps.payment.models import PromoCode, UserPromoCode
from .serializers import DiscountApplySerializer


class DiscountApplyView(GenericAPIView):
    """
    API endpoint to apply promo code and/or coins to get final price
    """
    serializer_class = DiscountApplySerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """Apply discounts and return final price"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        course_id = serializer.validated_data['course_id']
        promo_code = serializer.validated_data.get('promo_code')
        coins_to_use = serializer.validated_data.get('coins_to_use', 0)

        with transaction.atomic():
            # Get course with validation
            try:
                course = Course.objects.get(id=course_id, is_active=True, is_deleted=False)
            except Course.DoesNotExist:
                return Response({'error': 'Course not found, inactive, or deleted'}, status=status.HTTP_400_BAD_REQUEST)
            
            original_price = course.price  # Keep as Decimal

            # Initialize discount tracking
            promo_discount = 0
            coin_discount = 0
            promo_obj = None

            # Apply promo code discount if provided
            if promo_code:
                promo_obj = PromoCode.objects.get(code=promo_code)

                # Check if user has already used this promo code
                if UserPromoCode.objects.filter(
                        user=request.user,
                        promocode=promo_obj,
                        is_used=True
                ).exists():
                    return Response({
                        'error': 'You have already used this promo code'
                    }, status=status.HTTP_400_BAD_REQUEST)

            # Calculate promo discount (fixed amount, not percentage)
            if promo_obj:
                promo_discount = promo_obj.discount

            # Apply coin discount if provided
            if coins_to_use:
                coin_discount = coins_to_use

            # Calculate final price
            from decimal import Decimal
            total_discount = promo_discount + coin_discount
            final_price = original_price - Decimal(str(total_discount))
            
            # Ensure final price is not negative
            if final_price < 0:
                final_price = Decimal('0')

            # Don't mark promo code as used here - only when transaction is created

            # Prepare response
            response_data = {
                'course_id': course.id,
                'course_title': course.title,
                'original_price': float(original_price),
                'final_price': float(final_price),
                'total_discount': float(total_discount),
                'breakdown': {
                    'promo_discount': float(promo_discount),
                    'coin_discount': float(coin_discount),
                }
            }

            # Add promo code info if used
            if promo_obj:
                response_data['promo_code'] = promo_obj.code
                response_data['promo_discount_amount'] = promo_obj.discount

            # Add coin info if used
            if coins_to_use:
                response_data['coins_used'] = coins_to_use
                response_data['remaining_coins'] = request.user.coin - coins_to_use

            # Add success message
            if total_discount > 0:
                response_data['message'] = f'Discounts applied successfully! You saved {round(total_discount, 2)}'
            else:
                response_data['message'] = 'No discounts applied'

            return Response(response_data, status=status.HTTP_200_OK)


__all__ = ["DiscountApplyView"]
