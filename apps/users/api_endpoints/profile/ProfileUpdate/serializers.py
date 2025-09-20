from rest_framework import serializers

from apps.users.models import User


class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "full_name",
            "avatar",
            "username",
            "email",
            "grade",
            "birth_date",
            "region",
            "district",
            "address_index",
            "gender"
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
