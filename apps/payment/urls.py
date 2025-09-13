from django.urls import path, include

urlpatterns = [
    path("provider/", include("apps.payment.api_endpoints.providers.urls"))
]
