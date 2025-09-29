from django.core.cache import cache
from django.utils.translation import gettext_lazy as _
from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from apps.users.api_endpoints.auth.ForgetPassword.serializers import (
    ForgetPasswordSerializer,
)
from apps.users.models import User
from apps.users.services import CacheTypes, generate_cache_key


class ForgetPasswordView(generics.GenericAPIView):
    serializer_class = ForgetPasswordSerializer

    def post(self, request, *args, **kwargs):
        """
        Reset user password using OTP verification

        Required fields:
        - "phone": format E164 as like '+998945552233'
        - "code": 4-digit verification code from SMS
        - "session": session key from SendForgetPasswordCode API
        - "password": new password (min 8 characters)
        - "confirm_password": password confirmation
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data.get("phone")
        code = serializer.validated_data.get("code")
        session = serializer.validated_data.get("session")
        password = serializer.validated_data.get("password")

        # Validate OTP code
        cache_key = generate_cache_key(
            CacheTypes.forget_pass_sms_code, str(phone), session
        )

        if not self.is_code_valid(cache_key, code):
            raise ValidationError(detail={"code": _("Wrong code!")}, code="invalid")

        # Delete cache after successful verification
        cache.delete(cache_key)

        # Get user and update password
        try:
            user = User.objects.get(phone=phone)
            # Block TEACHER from resetting password via this endpoint
            if user.role == User.Role.TEACHER:
                raise ValidationError(
                    detail={
                        "role": _("Teacher accounts cannot reset password via this endpoint."),
                    },
                    code="forbidden",
                )
            user.set_password(password)
            user.save()
        except User.DoesNotExist:
            raise ValidationError(
                detail={"phone": _("User with this phone number does not exist.")},
                code="not_found",
            )

        return Response(
            {
                "message": _("Password has been reset successfully."),
                "success": True,
            }
        )

    @staticmethod
    def is_code_valid(cache_key, code):
        valid_code = cache.get(cache_key)
        if valid_code != code:
            return False
        return True


__all__ = ["ForgetPasswordView"]
