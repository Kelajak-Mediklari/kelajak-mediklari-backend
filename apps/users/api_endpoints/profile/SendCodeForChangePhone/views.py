from adrf.views import APIView
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db.transaction import non_atomic_requests
from django.utils.translation import gettext_lazy as _
from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.users.services import CacheTypes, MessageProvider

from .serializers import SendVerificationCodeForChangePhoneSerializer

User = get_user_model()


class SendCodeForChangePhoneView(APIView):
    """
    "phone": Send phone number in format E164 as like '+998945552233'
    """

    permission_classes = (IsAuthenticated,)

    @non_atomic_requests
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    @swagger_auto_schema(request_body=SendVerificationCodeForChangePhoneSerializer)
    async def post(self, request, *args, **kwargs):
        serializer = SendVerificationCodeForChangePhoneSerializer(data=request.data)
        await sync_to_async(serializer.is_valid)(raise_exception=True)

        phone = serializer.validated_data.get("phone")
        await sync_to_async(self.check_user_exists)(phone)

        # Use a rate limiting approach
        # Set a counter in the cache for this phone
        rate_limit_key = f"rate_limit:{CacheTypes.change_phone_sms_code}:{str(phone)}"

        # Get current counter value
        counter = await sync_to_async(cache.get)(rate_limit_key) or 0

        # Check if the counter exceeds the limit
        if counter >= 5:
            raise ValidationError(
                detail={
                    "send_verification_code_for_change_phone": _(
                        "You have reached the limit of sending verification code. Try again later."
                    )
                },
                code="limit_exceeded",
            )

        # Increment the counter and set it to expire after 120 seconds (same as code timeout)
        await sync_to_async(cache.set)(rate_limit_key, counter + 1, timeout=120)

        message_provider = MessageProvider(CacheTypes.change_phone_sms_code)
        await message_provider.send_sms(str(phone))
        return Response({"session": message_provider.session})

    @staticmethod
    def check_user_exists(phone):
        if User.objects.filter(phone=phone):
            raise ValidationError(
                detail={"phone": _("User with this phone already exists!")},
                code="unique",
            )


__all__ = ["SendCodeForChangePhoneView"]
