from django.contrib.auth.hashers import make_password
from django.utils.translation import gettext_lazy as _
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers


class RegisterSerializer(serializers.Serializer):
    phone = PhoneNumberField(region="UZ")
    full_name = serializers.CharField(max_length=255)
    password = serializers.CharField(min_length=8, max_length=128, write_only=True)
    device_id = serializers.CharField(max_length=255)
    code = serializers.CharField()
    session = serializers.CharField()

    def validate_password(self, value):
        """
        Validate password strength
        """
        if len(value) < 8:
            raise serializers.ValidationError(
                _("Password must be at least 8 characters long.")
            )
        return make_password(value)

    def validate_full_name(self, value):
        """
        Validate full name
        """
        if not value.strip():
            raise serializers.ValidationError(_("Full name cannot be empty."))
        return value.strip()
