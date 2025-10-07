from celery import shared_task
from django.utils import timezone
from django.db import transaction as db_transaction
from apps.payment.models import (
    CoinReservation, PromoCodeReservation, 
    Transaction, TransactionStatus
)


@shared_task(time_limit=300, bind=True)
def cleanup_expired_reservations(self):
    """
    Celery task to automatically clean up expired coin and promo code reservations.
    
    This task:
    1. Finds expired reservations (> 30 minutes old)
    2. Deactivates them
    3. Cancels associated pending transactions
    4. Cleans up old canceled transactions
    
    Should be run every 10 minutes via Celery Beat.
    """
    
    now = timezone.now()
    results = {
        'coin_reservations_cleaned': 0,
        'promo_reservations_cleaned': 0,
        'transactions_canceled': 0,
        'old_transactions_deleted': 0
    }
    
    try:
        with db_transaction.atomic():
            # Clean up expired coin reservations
            expired_coin_reservations = CoinReservation.objects.filter(
                is_active=True,
                expires_at__lt=now
            )
            
            for reservation in expired_coin_reservations:
                # Deactivate the reservation
                reservation.is_active = False
                reservation.save()
                
                # If transaction is still pending, cancel it
                if reservation.transaction and reservation.transaction.status == TransactionStatus.PENDING:
                    reservation.transaction.status = TransactionStatus.CANCELED
                    reservation.transaction.canceled_at = now
                    reservation.transaction.save()
                    results['transactions_canceled'] += 1
                
                results['coin_reservations_cleaned'] += 1
            
            # Clean up expired promo code reservations
            expired_promo_reservations = PromoCodeReservation.objects.filter(
                is_active=True,
                expires_at__lt=now
            )
            
            for reservation in expired_promo_reservations:
                # Deactivate the reservation
                reservation.is_active = False
                reservation.save()
                
                # If transaction is still pending, cancel it
                if reservation.transaction and reservation.transaction.status == TransactionStatus.PENDING:
                    reservation.transaction.status = TransactionStatus.CANCELED
                    reservation.transaction.canceled_at = now
                    reservation.transaction.save()
                    results['transactions_canceled'] += 1
                
                results['promo_reservations_cleaned'] += 1
            
            # Clean up old canceled transactions (older than 7 days)
            old_canceled_transactions = Transaction.objects.filter(
                status=TransactionStatus.CANCELED,
                canceled_at__lt=now - timezone.timedelta(days=7)
            )
            
            results['old_transactions_deleted'] = old_canceled_transactions.count()
            old_canceled_transactions.delete()
            
        # Return summary of what was cleaned up
        summary = (
            f"Cleanup completed: {results['coin_reservations_cleaned']} coin reservations, "
            f"{results['promo_reservations_cleaned']} promo reservations, "
            f"{results['transactions_canceled']} transactions canceled, "
            f"{results['old_transactions_deleted']} old transactions deleted"
        )
        
        return summary
        
    except Exception as exc:
        # Log the error and re-raise it so Celery can handle retries
        self.retry(countdown=60, max_retries=3, exc=exc)
