from adrf.views import APIView
from asgiref.sync import sync_to_async
from django.core.cache import cache
from django.db.transaction import non_atomic_requests
from django.utils.translation import gettext_lazy as _
from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from apps.users.api_endpoints.auth.SendAuthVerificationCode.serializers import (
    SendVerificationCodeSerializer,
)
from apps.users.services import CacheTypes, MessageProvider


class SendAuthVerificationCodeView(APIView):
    serializer_class = SendVerificationCodeSerializer

    @non_atomic_requests
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    @swagger_auto_schema(request_body=SendVerificationCodeSerializer)
    async def post(self, request, *args, **kwargs):
        """`phone` format E164 as like `+998945552233`"""
        serializer = self.serializer_class(data=request.data)
        await sync_to_async(serializer.is_valid)(raise_exception=True)
        phone = serializer.validated_data.get("phone", None)
        email = serializer.validated_data.get("email", None)

        # We'll use a rate limiting approach
        # Set a counter in the cache for this phone or email
        if phone:
            rate_limit_key = f"rate_limit:{CacheTypes.auth_sms_code}:{str(phone)}"
        else:
            rate_limit_key = f"rate_limit:{CacheTypes.auth_sms_code}:{str(email)}"

        # Get current counter value
        counter = await sync_to_async(cache.get)(rate_limit_key) or 0

        # Check if the counter exceeds the limit
        if counter >= 5:
            raise ValidationError(
                detail={
                    "send_verification_code": _(
                        "You have reached the limit of sending verification code. Try again later."
                    )
                },
                code="limit_exceeded",
            )

        # Increment the counter and set it to expire after 120 seconds (same as code timeout)
        await sync_to_async(cache.set)(rate_limit_key, counter + 1, timeout=120)

        message_provider = MessageProvider(CacheTypes.auth_sms_code)

        if phone:
            await message_provider.send_sms(str(phone))
        else:
            await message_provider.send_email(str(email), "email/auth_sms_code.html")

        return Response({"session": message_provider.session})


__all__ = ["SendAuthVerificationCodeView"]
