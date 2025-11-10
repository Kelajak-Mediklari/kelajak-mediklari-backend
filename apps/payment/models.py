from click_up import ClickUp
from django.conf import settings
from django.db import models
from django.db import transaction as db_transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from payme import Payme

from apps.common.models import BaseModel

click_up = ClickUp(
    service_id=settings.CLICK_SERVICE_ID, merchant_id=settings.CLICK_MERCHANT_ID
)
payme = Payme(payme_id=settings.PAYME_ID)


class PaymentProvider(models.TextChoices):
    PAYME = "Payme", _("Payme")
    CLICK = "Click", _("Click")


class TransactionStatus(models.TextChoices):
    PENDING = "pending", _("pending")
    CREATED = "created", _("created")
    SUCCESS = "success", _("success")
    FAILED = "failed", _("failed")
    REJECTED = "rejected", _("rejected")
    CANCELED = "canceled", _("canceled")


class Transaction(BaseModel):
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="t_users",
        verbose_name=_("user"),
    )
    course = models.ForeignKey(
        "course.Course",
        on_delete=models.CASCADE,
        related_name="t_courses",
        verbose_name=_("courses"),
    )
    amount = models.DecimalField(
        max_digits=12, decimal_places=2, verbose_name=_("amount")
    )
    provider = models.CharField(
        max_length=50,
        choices=PaymentProvider.choices,
        verbose_name=_("provider"),
        null=True,
        blank=True,
    )
    duration = models.IntegerField(_("duration in month"), null=True)
    paid_at = models.DateTimeField(verbose_name=_("paid at"), null=True, blank=True)
    canceled_at = models.DateTimeField(
        verbose_name=_("canceled at"), null=True, blank=True
    )
    status = models.CharField(
        max_length=20, choices=TransactionStatus.choices, verbose_name=_("status")
    )

    # Discount fields
    original_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name=_("original amount"),
        null=True,
        blank=True,
        help_text=_("Original course price before discounts"),
    )
    promo_code = models.CharField(
        max_length=255,
        verbose_name=_("promo code"),
        null=True,
        blank=True,
        help_text=_("Promo code used in this transaction"),
    )
    promo_discount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name=_("promo discount"),
        null=True,
        blank=True,
        default=0,
        help_text=_("Discount amount from promo code"),
    )
    coins_used = models.IntegerField(
        verbose_name=_("coins used"),
        null=True,
        blank=True,
        default=0,
        help_text=_("Number of coins used in this transaction"),
    )

    def __str__(self):
        return f"{self.user.full_name}:{self.course.title}"

    class Meta:
        verbose_name = _("Transaction")
        verbose_name_plural = _("Transactions")

    def success_process(self):
        with db_transaction.atomic():
            self.paid_at = timezone.now()
            self.status = TransactionStatus.SUCCESS
            self.save(update_fields=["paid_at", "status"])

            # Create UserCourse with calculated finish_date
            from datetime import timedelta

            from django.utils import timezone as django_timezone

            from apps.course.models import UserCourse

            # Calculate finish_date based on duration in months
            start_date = django_timezone.now()
            finish_date = (
                start_date + timedelta(days=self.duration * 30)
                if self.duration
                else None
            )

            # Create or update UserCourse
            # This is a paid course, so set is_free_trial=False
            user_course, created = UserCourse.objects.update_or_create(
                user=self.user,
                course=self.course,
                defaults={
                    "start_date": start_date,
                    "finish_date": finish_date,
                    "is_expired": False,
                    "is_free_trial": False,
                },
            )

    def cancel_process(self):
        with db_transaction.atomic():
            self.canceled_at = timezone.now()
            self.status = TransactionStatus.CANCELED
            self.save(update_fields=["canceled_at", "status"])

    @property
    def payment_url(self):
        payment_url = ""
        if self.provider == PaymentProvider.PAYME:
            payment_url = payme.initializer.generate_pay_link(
                id=self.id,
                amount=self.amount,
                return_url=f"https://kelajakmediklari.uz/",
            )
            print(payment_url)
        elif self.provider == PaymentProvider.CLICK:
            payment_url = click_up.initializer.generate_pay_link(
                id=self.id,
                amount=self.amount,
                return_url="https://kelajakmediklari.uz/",
            )

        return payment_url


class PromoCode(BaseModel):
    code = models.CharField(max_length=255, verbose_name=_("code"))
    discount = models.IntegerField(verbose_name=_("discount"))
    courses = models.ManyToManyField(
        "course.Course", verbose_name=_("courses"), related_name="promocodes"
    )
    is_active = models.BooleanField(default=True, verbose_name=_("is active"))

    def __str__(self):
        return self.code

    class Meta:
        verbose_name = _("PromoCode")
        verbose_name_plural = _("PromoCodes")


class UserPromoCode(BaseModel):
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="up_users",
        verbose_name=_("user"),
    )
    promocode = models.ForeignKey(
        "payment.PromoCode",
        on_delete=models.CASCADE,
        related_name="up_promocodes",
        verbose_name=_("promocode"),
    )
    is_used = models.BooleanField(default=True, verbose_name=_("is used"))
    transaction = models.ForeignKey(
        "payment.Transaction",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_("transaction"),
        help_text=_("Transaction that used this promo code"),
    )

    def __str__(self):
        return f"{self.user.full_name}:{self.promocode.code}"

    class Meta:
        verbose_name = _("User PromoCode")
        verbose_name_plural = _("User PromoCode")


class CoinReservation(BaseModel):
    """Temporary coin reservation for pending transactions"""

    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="coin_reservations",
        verbose_name=_("user"),
    )
    amount = models.PositiveIntegerField(
        verbose_name=_("amount"), help_text=_("Amount of coins reserved")
    )
    transaction = models.ForeignKey(
        "payment.Transaction",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_("transaction"),
        help_text=_("Transaction that reserved these coins"),
    )
    expires_at = models.DateTimeField(
        verbose_name=_("expires at"), help_text=_("When this reservation expires")
    )
    is_active = models.BooleanField(default=True, verbose_name=_("is active"))

    def __str__(self):
        return f"{self.user.full_name}: {self.amount} coins (expires {self.expires_at})"

    class Meta:
        verbose_name = _("Coin Reservation")
        verbose_name_plural = _("Coin Reservations")


class PromoCodeReservation(BaseModel):
    """Temporary promo code reservation for pending transactions"""

    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="promo_reservations",
        verbose_name=_("user"),
    )
    promocode = models.ForeignKey(
        "payment.PromoCode", on_delete=models.CASCADE, verbose_name=_("promo code")
    )
    transaction = models.ForeignKey(
        "payment.Transaction",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_("transaction"),
        help_text=_("Transaction that reserved this promo code"),
    )
    expires_at = models.DateTimeField(
        verbose_name=_("expires at"), help_text=_("When this reservation expires")
    )
    is_active = models.BooleanField(default=True, verbose_name=_("is active"))

    def __str__(self):
        return (
            f"{self.user.full_name}: {self.promocode.code} (expires {self.expires_at})"
        )

    class Meta:
        verbose_name = _("Promo Code Reservation")
        verbose_name_plural = _("Promo Code Reservations")
