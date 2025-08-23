from adrf.serializers import Serializer
from django.utils.translation import gettext_lazy as _
from phonenumber_field.validators import validate_international_phonenumber
from rest_framework import serializers


class SendVerificationCodeSerializer(Serializer):
    phone = serializers.CharField(
        validators=[validate_international_phonenumber], required=False
    )
    email = serializers.EmailField(required=False)

    def validate_email(self, email):
        return email.lower()

    def validate(self, attrs):
        if not attrs.get("phone") and not attrs.get("email"):
            raise serializers.ValidationError(
                detail={
                    "email": _("Email or phone is required"),
                    "phone": _("Phone or email is required"),
                },
                code="required",
            )
        if attrs.get("phone") and attrs.get("email"):
            raise serializers.ValidationError(
                detail={
                    "email": _("Email and phone can't be used together"),
                    "phone": _("Phone and email can't be used together"),
                },
                code="too_many_fields",
            )
        return attrs
