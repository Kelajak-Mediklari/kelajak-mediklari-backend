from django.utils.translation import gettext_lazy as _
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers


class CheckPhoneSerializer(serializers.Serializer):
    phone = PhoneNumberField(region="UZ", required=True)

    def validate_phone(self, value):
        """
        Validate that phone number is provided
        """
        if not value:
            raise serializers.ValidationError(_("Phone number is required."))
        return value
