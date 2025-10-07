from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.payment.models import (
    CoinReservation, PromoCodeReservation, 
    Transaction, TransactionStatus
)


class Command(BaseCommand):
    help = 'Clean up expired coin and promo code reservations'

    def handle(self, *args, **options):
        now = timezone.now()
        
        # Clean up expired coin reservations
        expired_coin_reservations = CoinReservation.objects.filter(
            is_active=True,
            expires_at__lt=now
        )
        
        coin_count = 0
        for reservation in expired_coin_reservations:
            # Deactivate the reservation
            reservation.is_active = False
            reservation.save()
            
            # If transaction is still pending, cancel it
            if reservation.transaction and reservation.transaction.status == TransactionStatus.PENDING:
                reservation.transaction.status = TransactionStatus.CANCELED
                reservation.transaction.canceled_at = now
                reservation.transaction.save()
            
            coin_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'Cleaned up {coin_count} expired coin reservations')
        )
        
        # Clean up expired promo code reservations
        expired_promo_reservations = PromoCodeReservation.objects.filter(
            is_active=True,
            expires_at__lt=now
        )
        
        promo_count = 0
        for reservation in expired_promo_reservations:
            # Deactivate the reservation
            reservation.is_active = False
            reservation.save()
            
            # If transaction is still pending, cancel it
            if reservation.transaction and reservation.transaction.status == TransactionStatus.PENDING:
                reservation.transaction.status = TransactionStatus.CANCELED
                reservation.transaction.canceled_at = now
                reservation.transaction.save()
            
            promo_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'Cleaned up {promo_count} expired promo code reservations')
        )
        
        # Clean up old canceled transactions with expired reservations
        old_canceled_transactions = Transaction.objects.filter(
            status=TransactionStatus.CANCELED,
            canceled_at__lt=now - timezone.timedelta(days=7)  # 7 days old
        )
        
        old_count = old_canceled_transactions.count()
        old_canceled_transactions.delete()
        
        self.stdout.write(
            self.style.SUCCESS(f'Cleaned up {old_count} old canceled transactions')
        )
