from click_up.views import ClickWebhook
from click_up.models import ClickTransaction

from rest_framework.permissions import AllowAny

from apps.payment.models import Transaction


class ClickWebhookAPIView(ClickWebhook):
    permission_classes = [AllowAny]

    def successfully_payment(self, params):
        """
        successfully payment method process you can ovveride it
        """
        click_trans_id = params.click_trans_id
        print(click_trans_id)

        try:
            click_transaction = ClickTransaction.objects.get(transaction_id=click_trans_id)
        except ClickTransaction.DoesNotExist:
            raise Exception("ClickTransaction not found")

        account_id = click_transaction.account_id
        print(account_id)

        try:
            transaction = Transaction.objects.get(id=account_id)
        except Transaction.DoesNotExist:
            raise Exception("Transaction not found for account_id")

        transaction.success_process()

    def cancelled_payment(self, params):
        """
        cancelled payment method process you can ovveride it
        """
        click_trans_id = params.click_trans_id

        try:
            click_transaction = ClickTransaction.objects.get(transaction_id=click_trans_id)
        except ClickTransaction.DoesNotExist:
            raise Exception("ClickTransaction not found")

        account_id = click_transaction.account_id
        print(account_id)

        try:
            transaction = Transaction.objects.get(id=account_id)
        except Transaction.DoesNotExist:
            raise Exception("Transaction not found for account_id")

        transaction.cancel_process()
