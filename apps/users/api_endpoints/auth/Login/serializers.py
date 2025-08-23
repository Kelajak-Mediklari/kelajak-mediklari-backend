from django.utils.translation import gettext_lazy as _
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers


class LoginSerializer(serializers.Serializer):
    phone = PhoneNumberField(region="UZ", required=True)
    password = serializers.CharField(required=True, write_only=True)
    device_id = serializers.CharField(max_length=255, required=True)

    def validate_phone(self, value):
        """
        Validate that phone number is provided
        """
        if not value:
            raise serializers.ValidationError(_("Phone number is required."))
        return value

    def validate_password(self, value):
        """
        Validate that password is provided
        """
        if not value:
            raise serializers.ValidationError(_("Password is required."))
        return value
