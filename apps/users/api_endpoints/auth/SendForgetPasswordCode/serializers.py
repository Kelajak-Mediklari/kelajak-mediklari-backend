from adrf.serializers import Serializer
from django.utils.translation import gettext_lazy as _
from phonenumber_field.validators import validate_international_phonenumber
from rest_framework import serializers

from apps.users.models import User


class SendForgetPasswordCodeSerializer(Serializer):
    phone = serializers.CharField(
        validators=[validate_international_phonenumber], required=True
    )

    def validate_phone(self, phone):
        # Check if user with this phone exists
        if not User.objects.filter(phone=phone).exists():
            raise serializers.ValidationError(
                detail=_("User with this phone number does not exist."),
                code="not_found",
            )
        return phone
