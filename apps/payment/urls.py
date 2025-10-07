from django.urls import path, include
from apps.payment.api_endpoints.payment.TransactionCreate.views import TransactionCreateAPIView
from apps.payment.api_endpoints.payment.TransactionList.views import TransactionListAPIView
from apps.payment.api_endpoints.payment.TransactionDetail.views import TransactionDetailAPIView
from apps.payment.api_endpoints.payment.DiscountApply.views import DiscountApplyView
from apps.payment.api_endpoints.payment.PaymentCallback.views import PaymentCallbackView

urlpatterns = [
    path("provider/", include("apps.payment.api_endpoints.providers.urls")),
    path("transaction/create/", TransactionCreateAPIView.as_view(), name="transaction-create"),
    path("transaction/list/", TransactionListAPIView.as_view(), name="transaction-list"),
    path("transaction/<int:transaction_id>/", TransactionDetailAPIView.as_view(), name="transaction-detail"),
    path("discount/apply/", DiscountApplyView.as_view(), name="discount-apply"),
    path("callback/", PaymentCallbackView.as_view(), name="payment-callback"),
]
