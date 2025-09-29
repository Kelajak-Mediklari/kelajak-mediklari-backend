from adrf.views import APIView
from asgiref.sync import sync_to_async
from django.core.cache import cache
from django.db.transaction import non_atomic_requests
from django.utils.translation import gettext_lazy as _
from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from apps.users.api_endpoints.auth.SendForgetPasswordCode.serializers import (
    SendForgetPasswordCodeSerializer,
)
from apps.users.models import User
from apps.users.services import CacheTypes, MessageProvider


class SendForgetPasswordCodeView(APIView):
    serializer_class = SendForgetPasswordCodeSerializer

    @non_atomic_requests
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    @swagger_auto_schema(request_body=SendForgetPasswordCodeSerializer)
    async def post(self, request, *args, **kwargs):
        """Send OTP code to phone for password reset

        Required fields:
        - "phone": format E164 as like '+998945552233'
        """
        serializer = self.serializer_class(data=request.data)
        await sync_to_async(serializer.is_valid)(raise_exception=True)
        phone = serializer.validated_data.get("phone")

        # Block TEACHER from receiving forget password OTP
        try:
            user = await sync_to_async(User.objects.get)(phone=phone)
            if user.role == User.Role.TEACHER:
                raise ValidationError(
                    detail={
                        "role": _("Teacher accounts cannot reset password via this endpoint."),
                    },
                    code="forbidden",
                )
        except User.DoesNotExist:
            pass

        # Rate limiting approach
        rate_limit_key = f"rate_limit:{CacheTypes.forget_pass_sms_code}:{str(phone)}"

        # Get current counter value
        counter = await sync_to_async(cache.get)(rate_limit_key) or 0

        # Check if the counter exceeds the limit (5 requests per 2 minutes)
        if counter >= 5:
            raise ValidationError(
                detail={
                    "send_forget_password_code": _(
                        "You have reached the limit of sending forget password code. Try again later."
                    )
                },
                code="limit_exceeded",
            )

        # Increment the counter and set it to expire after 120 seconds
        await sync_to_async(cache.set)(rate_limit_key, counter + 1, timeout=120)

        message_provider = MessageProvider(CacheTypes.forget_pass_sms_code)
        await message_provider.send_sms(str(phone))

        return Response({"session": message_provider.session})


__all__ = ["SendForgetPasswordCodeView"]
