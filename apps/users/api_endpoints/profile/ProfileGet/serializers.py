from rest_framework import serializers

from apps.users.models import User


class ProfileGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "full_name", "username", "phone", "avatar"]
