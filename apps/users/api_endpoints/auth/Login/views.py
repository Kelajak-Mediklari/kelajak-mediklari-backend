from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import update_last_login
from django.utils.translation import gettext_lazy as _
from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.api_endpoints.auth.Login.serializers import LoginSerializer
from apps.users.models import User, UserDevice


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        """
        Login with phone number and password

        Required fields:
        - "phone": format E164 as like '+998945552233'
        - "password": user's password
        - "device_id": unique device identifier
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data.get("phone")
        password = serializer.validated_data.get("password")
        device_id = serializer.validated_data.get("device_id")

        # Check if user exists
        try:
            user = User.objects.get(phone=phone)
        except User.DoesNotExist:
            raise ValidationError(
                detail={"phone": _("User with this phone number does not exist.")},
                code="not_found",
            )

        # Check password
        if not user.password or not check_password(password, user.password):
            raise ValidationError(
                detail={"password": _("Invalid password.")}, code="invalid_credentials"
            )

        # Generate tokens
        token = RefreshToken.for_user(user)

        # Update or create user device and set device_id to refresh and access token
        UserDevice.objects.update_or_create(
            user=user, device_id=device_id, defaults={"is_active": True}
        )
        token["device_id"] = device_id

        # Inactivate other last 2 devices
        last_active_devices = (
            user.devices.exclude(device_id=device_id)
            .filter(is_active=True)
            .order_by("-updated_at")
        )
        if last_active_devices.exists():
            latest_device = last_active_devices.first()
            last_active_devices.exclude(id=latest_device.id).update(is_active=False)

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
            "created": False,
        }

        # Update last login
        update_last_login(None, user)

        return Response(response_data)


__all__ = ["LoginView"]
