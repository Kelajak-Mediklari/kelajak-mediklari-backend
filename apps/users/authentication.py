from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication


class CustomJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        user = super().get_user(validated_token)

        if user.is_deleted:
            raise AuthenticationFailed(_("User is deleted"))

        device_id = validated_token.get("device_id", None)
        if device_id:
            device = user.devices.filter(
                device_id=validated_token.get("device_id"), is_active=True
            )
            if not device.exists():
                raise AuthenticationFailed(_("Device is not active or not found"))

        return user