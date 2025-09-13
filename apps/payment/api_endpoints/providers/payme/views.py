from payme.types import response
from payme.views import PaymeWebHookAPIView
from payme.models import PaymeTransactions
from django.utils import timezone
from apps.payment.models import Transaction


# pylint: disable=E1101
class PaymeCallBackAPIView(PaymeWebHookAPIView):
    """
    A view to handle Payme Webhook API calls.
    This view will handle all the Payme Webhook API events.
    """

    def check_perform_transaction(self, params):
        account = self.fetch_account(params)
        self.validate_amount(account, params.get('amount'))

        result = response.CheckPerformTransaction(allow=True)

        return result.as_resp()

    def handle_successfully_payment(self, params, result, *args, **kwargs):
        """
        Handle the successful payment. You can override this method
        """
        transaction = PaymeTransactions.get_by_transaction_id(
            transaction_id=params["id"]
        )

        order = Transaction.objects.get(id=transaction.account_id)
        order.success_process()

    def handle_cancelled_payment(self, params, result, *args, **kwargs):
        """
        Handle the cancelled payment. You can override this method
        """
        transaction = PaymeTransactions.get_by_transaction_id(
            transaction_id=params["id"]
        )

        if transaction.state == PaymeTransactions.CANCELED:
            order = Transaction.objects.get(id=transaction.account_id)
            order.cancel_process()
