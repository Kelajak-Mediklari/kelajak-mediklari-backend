from django.contrib.auth.models import update_last_login
from django.core.cache import cache
from django.utils.translation import gettext_lazy as _
from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.api_endpoints.auth.Register.serializers import RegisterSerializer
from apps.users.models import User, UserDevice
from apps.users.services import CacheTypes, generate_cache_key


class RegisterView(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        """
        Register a new user with phone verification

        Required fields:
        - "phone": format E164 as like '+998945552233'
        - "full_name": user's full name
        - "password": user's password (min 8 characters)
        - "device_id": unique device identifier
        - "code": verification code from SMS
        - "session": session key from SendAuthVerificationCode API
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data.get("phone")
        full_name = serializer.validated_data.get("full_name")
        password = serializer.validated_data.get("password")
        device_id = serializer.validated_data.get("device_id")
        code = serializer.validated_data.get("code")
        session = serializer.validated_data.get("session")

        # Check if user already exists
        if User.objects.filter(phone=phone).exists():
            raise ValidationError(
                detail={"phone": _("User with this phone number already exists.")},
                code="already_exists",
            )

        # Validate OTP code
        cache_key = generate_cache_key(CacheTypes.auth_sms_code, str(phone), session)

        if not self.is_code_valid(cache_key, code):
            raise ValidationError(detail={"code": _("Wrong code!")}, code="invalid")

        # Delete cache after successful verification
        cache.delete(cache_key)

        # Create new user
        user = User.objects.create(
            phone=phone,
            full_name=full_name,
            password=password,
            username=User.generate_username(full_name),
        )

        # Generate tokens
        token = RefreshToken.for_user(user)

        # Create user device
        UserDevice.objects.create(user=user, device_id=device_id, is_active=True)
        token["device_id"] = device_id

        response_data = {
            "refresh": str(token),
            "access": str(token.access_token),
            "user": {
                "id": user.id,
                "full_name": user.full_name,
                "username": user.username,
                "phone": str(user.phone),
                "avatar": request.build_absolute_uri(user.avatar.url)
                if user.avatar
                else None,
            },
            "created": True,
        }

        # Update last login
        update_last_login(None, user)

        return Response(response_data)

    @staticmethod
    def is_code_valid(cache_key, code):
        valid_code = cache.get(cache_key)
        if valid_code != code:
            return False
        return True


__all__ = ["RegisterView"]
