from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction as db_transaction
from django.utils import timezone
from datetime import timedelta

from apps.payment.models import Transaction, TransactionStatus, PromoCode, UserPromoCode, CoinReservation, PromoCodeReservation
from apps.course.models import Course
from apps.payment.api_endpoints.payment.TransactionCreate.serializers import TransactionCreateSerializer


class TransactionCreateAPIView(CreateAPIView):
    """
    API endpoint to create a new transaction
    """
    serializer_class = TransactionCreateSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Get course from validated data (already validated in serializer)
        course = Course.objects.get(id=serializer.validated_data['course_id'])
        
        # Extract discount information
        promo_code = serializer.validated_data.get('promo_code')
        coins_used = serializer.validated_data.get('coins_used', 0)
        bypass_validation = serializer.validated_data.get('bypass_validation', False)
        
        # Use atomic transaction for security
        with db_transaction.atomic():
            # Calculate discount amounts if bypass_validation is used
            original_amount = course.price  # Keep as Decimal
            promo_discount = 0
            promo_obj = None
            
            # Create transaction first
            transaction = Transaction.objects.create(
                user=request.user,
                course=course,
                amount=serializer.validated_data['amount'],
                provider=serializer.validated_data['provider'],
                duration=serializer.validated_data['duration'],
                status=TransactionStatus.PENDING,
                # Discount fields
                original_amount=original_amount,
                promo_code=promo_code,
                promo_discount=promo_discount,
                coins_used=coins_used
            )
            
            # Create reservations for coins and promo codes (don't deduct yet)
            if bypass_validation and promo_code:
                promo_obj = PromoCode.objects.get(code=promo_code)
                promo_discount = promo_obj.discount  # Fixed amount, not percentage
                
                # Create promo code reservation (not used yet)
                PromoCodeReservation.objects.create(
                    user=request.user,
                    promocode=promo_obj,
                    transaction=transaction,
                    expires_at=timezone.now() + timedelta(minutes=30),  # Expires in 30 minutes
                    is_active=True
                )
                
                # Update transaction with promo discount
                transaction.promo_discount = promo_discount
                transaction.save()
            
            # Create coin reservation (don't deduct yet)
            if bypass_validation and coins_used:
                CoinReservation.objects.create(
                    user=request.user,
                    amount=coins_used,
                    transaction=transaction,
                    expires_at=timezone.now() + timedelta(minutes=30),  # Expires in 30 minutes
                    is_active=True
                )

        # Generate payment URL
        payment_url = transaction.payment_url

        return Response({
            'transaction_id': transaction.id,
            'course_id': course.id,
            'amount': transaction.amount,
            'provider': transaction.provider,
            'payment_url': payment_url,
            'original_amount': transaction.original_amount,
            'promo_code': transaction.promo_code,
            'promo_discount': transaction.promo_discount,
            'coins_used': transaction.coins_used
        }, status=status.HTTP_201_CREATED)
