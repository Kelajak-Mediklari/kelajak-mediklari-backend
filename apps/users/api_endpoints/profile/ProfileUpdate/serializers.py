from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import serializers

from apps.users.models import User


class ProfileUpdateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=False, style={"input_type": "password"}
    )
    confirm_password = serializers.CharField(
        write_only=True, required=False, style={"input_type": "password"}
    )
    current_password = serializers.CharField(
        write_only=True, required=False, style={"input_type": "password"}
    )

    class Meta:
        model = User
        fields = [
            "full_name",
            "avatar",
            "grade",
            "birth_date",
            "region",
            "district",
            "address_index",
            "gender",
            "password",
            "confirm_password",
            "current_password",
        ]
        extra_kwargs = {
            "full_name": {"required": False}, 
            "avatar": {"required": False},
            "grade": {"required": False},
            "birth_date": {"required": False},
            "region": {"required": False},
            "district": {"required": False},
            "address_index": {"required": False},
            "gender": {"required": False},
        }

    def validate(self, attrs):
        password = attrs.get("password")
        confirm_password = attrs.get("confirm_password")
        current_password = attrs.get("current_password")

        # If password is being updated
        if password:
            # Check if current password is provided
            if not current_password:
                raise serializers.ValidationError(
                    {
                        "current_password": "Current password is required to update password."
                    }
                )

            # Verify current password
            if not self.instance.check_password(current_password):
                raise serializers.ValidationError(
                    {"current_password": "Current password is incorrect."}
                )

            # Check if password and confirm_password match
            if password != confirm_password:
                raise serializers.ValidationError(
                    {"confirm_password": "Password and confirm password do not match."}
                )

            # Validate password strength
            try:
                validate_password(password, self.instance)
            except ValidationError as e:
                raise serializers.ValidationError({"password": list(e.messages)})

        # Remove confirm_password and current_password from attrs since they're not model fields
        attrs.pop("confirm_password", None)
        attrs.pop("current_password", None)

        return attrs

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)

        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Update password if provided
        if password:
            instance.set_password(password)

        instance.save()
        return instance
