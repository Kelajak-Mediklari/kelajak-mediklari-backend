from adrf.serializers import Serializer
from django.utils.translation import gettext_lazy as _
from phonenumber_field.validators import validate_international_phonenumber
from rest_framework import serializers


class SendVerificationCodeSerializer(Serializer):
    phone = serializers.CharField(
        validators=[validate_international_phonenumber], required=True
    )

    def validate_phone(self, value):
        """
        Validate that phone number is provided
        """
        if not value:
            raise serializers.ValidationError(_("Phone number is required."))
        return value
