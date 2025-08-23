from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from phonenumber_field.validators import validate_international_phonenumber
from rest_framework import serializers

from apps.users.models import User


class ForgetPasswordSerializer(serializers.Serializer):
    phone = serializers.CharField(
        validators=[validate_international_phonenumber], required=True
    )
    code = serializers.CharField(max_length=4, min_length=4, required=True)
    session = serializers.CharField(max_length=16, min_length=16, required=True)
    password = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )
    confirm_password = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )

    def validate_phone(self, phone):
        # Check if user with this phone exists
        try:
            user = User.objects.get(phone=phone)
            return phone
        except User.DoesNotExist:
            raise serializers.ValidationError(
                "User with this phone number does not exist."
            )

    def validate(self, attrs):
        password = attrs.get("password")
        confirm_password = attrs.get("confirm_password")
        phone = attrs.get("phone")

        # Check if passwords match
        if password != confirm_password:
            raise serializers.ValidationError(
                {"confirm_password": "Password and confirm password do not match."}
            )

        # Validate password strength
        try:
            user = User.objects.get(phone=phone)
            validate_password(password, user)
        except ValidationError as e:
            raise serializers.ValidationError({"password": list(e.messages)})

        # Remove confirm_password from attrs since it's not needed in the view
        attrs.pop("confirm_password", None)

        return attrs
