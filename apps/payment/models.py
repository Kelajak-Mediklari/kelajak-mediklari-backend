from apps.common.models import BaseModel
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.db import transaction as db_transaction
from django.utils import timezone
from click_up import ClickUp
from payme import Payme
from django.conf import settings

click_up = ClickUp(service_id=settings.CLICK_SERVICE_ID, merchant_id=settings.CLICK_MERCHANT_ID)
payme = Payme(
    payme_id=settings.PAYME_ID
)


class PaymentProvider(models.TextChoices):
    PAYME = 'Payme', _('Payme')
    CLICK = 'Click', _('Click')


class TransactionStatus(models.TextChoices):
    PENDING = 'pending', _('pending')
    CREATED = 'created', _('created')
    SUCCESS = 'success', _('success')
    FAILED = 'failed', _('failed')
    REJECTED = 'rejected', _('rejected')
    CANCELED = 'canceled', _('canceled')


class Transaction(BaseModel):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="t_users", verbose_name=_("user"))
    course = models.ForeignKey("course.Course", on_delete=models.CASCADE, related_name="t_courses",
                               verbose_name=_("courses"))
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name=_('amount'))
    provider = models.CharField(max_length=50, choices=PaymentProvider.choices, verbose_name=_('provider'),
                                null=True, blank=True)
    duration = models.IntegerField(_("duration in month"), null=True)
    paid_at = models.DateTimeField(verbose_name=_('paid at'), null=True, blank=True)
    canceled_at = models.DateTimeField(verbose_name=_('canceled at'), null=True, blank=True)
    status = models.CharField(max_length=20, choices=TransactionStatus.choices, verbose_name=_("status"))

    def __str__(self):
        return f'{self.user.full_name}:{self.course.title}'

    class Meta:
        verbose_name = _("Transaction")
        verbose_name_plural = _("Transactions")

    def success_process(self):
        with db_transaction.atomic():
            self.paid_at = timezone.now()
            self.status = TransactionStatus.SUCCESS
            self.save(update_fields=['paid_at', 'status'])

            # Create UserCourse with calculated finish_date
            from apps.course.models import UserCourse
            from django.utils import timezone as django_timezone
            from datetime import timedelta

            # Calculate finish_date based on duration in months
            start_date = django_timezone.now()
            finish_date = start_date + timedelta(days=self.duration * 30) if self.duration else None

            # Create or update UserCourse
            user_course, created = UserCourse.objects.update_or_create(
                user=self.user,
                course=self.course,
                defaults={
                    'start_date': start_date,
                    'finish_date': finish_date,
                    'is_expired': False,
                }
            )

    def cancel_process(self):
        with db_transaction.atomic():
            self.canceled_at = timezone.now()
            self.status = TransactionStatus.CANCELED
            self.save(update_fields=['canceled_at', 'status'])

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
                return_url="https://kelajakmediklari.uz/"
            )

        return payment_url
