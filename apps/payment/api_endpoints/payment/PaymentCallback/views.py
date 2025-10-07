from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction as db_transaction
from django.utils import timezone

from apps.payment.models import (
    Transaction, TransactionStatus, CoinReservation, 
    PromoCodeReservation, UserPromoCode
)


class PaymentCallbackView(APIView):
    """
    Handle payment success/failure callbacks from payment gateways
    This is where we actually deduct coins and mark promo codes as used
    """
    
    def post(self, request, *args, **kwargs):
        transaction_id = request.data.get('transaction_id')
        is_successful = request.data.get('success', False)
        
        try:
            transaction = Transaction.objects.get(id=transaction_id)
        except Transaction.DoesNotExist:
            return Response({'error': 'Transaction not found'}, status=status.HTTP_404_NOT_FOUND)
        
        with db_transaction.atomic():
            if is_successful:
                # Payment successful - now actually deduct coins and mark promo codes as used
                self._process_successful_payment(transaction)
                
                return Response({
                    'status': 'success',
                    'message': 'Payment processed successfully',
                    'transaction_id': transaction.id
                })
            else:
                # Payment failed - release reserved resources
                self._process_failed_payment(transaction)
                
                return Response({
                    'status': 'failed',
                    'message': 'Payment failed, resources released',
                    'transaction_id': transaction.id
                })
    
    def _process_successful_payment(self, transaction):
        """Process successful payment - deduct coins and mark promo codes as used"""
        
        # Mark transaction as paid
        transaction.status = TransactionStatus.PAID
        transaction.paid_at = timezone.now()
        transaction.save()
        
        # Actually deduct coins from user balance
        if transaction.coins_used and transaction.coins_used > 0:
            # Find and process coin reservation
            coin_reservation = CoinReservation.objects.filter(
                transaction=transaction,
                is_active=True
            ).first()
            
            if coin_reservation:
                # Actually deduct coins from user
                transaction.user.subtract_coins(transaction.coins_used)
                # Mark reservation as used
                coin_reservation.is_active = False
                coin_reservation.save()
        
        # Mark promo code as actually used
        if transaction.promo_code:
            promo_reservation = PromoCodeReservation.objects.filter(
                transaction=transaction,
                is_active=True
            ).first()
            
            if promo_reservation:
                # Create actual UserPromoCode record (mark as used)
                UserPromoCode.objects.create(
                    user=transaction.user,
                    promocode=promo_reservation.promocode,
                    is_used=True,
                    transaction=transaction
                )
                # Mark reservation as used
                promo_reservation.is_active = False
                promo_reservation.save()
    
    def _process_failed_payment(self, transaction):
        """Process failed payment - release reserved resources"""
        
        # Mark transaction as canceled
        transaction.status = TransactionStatus.CANCELED
        transaction.canceled_at = timezone.now()
        transaction.save()
        
        # Release coin reservations
        CoinReservation.objects.filter(
            transaction=transaction,
            is_active=True
        ).update(is_active=False)
        
        # Release promo code reservations
        PromoCodeReservation.objects.filter(
            transaction=transaction,
            is_active=True
        ).update(is_active=False)
