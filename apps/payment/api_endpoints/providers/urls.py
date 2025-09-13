from django.urls import path

from apps.payment.api_endpoints.providers.click.views import ClickWebhookAPIView
from apps.payment.api_endpoints.providers.payme.views import PaymeCallBackAPIView

urlpatterns = [
    path(
        "click/update/",
        ClickWebhookAPIView.as_view(),
        name="click-merchant-callback"
    ),

    path(
        "payme/",
        PaymeCallBackAPIView.as_view(),
        name="payme-merchant-callback",
    ),

]
