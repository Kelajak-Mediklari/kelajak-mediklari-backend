from phonenumber_field.validators import validate_international_phonenumber
from rest_framework import serializers


class UserChangePhoneSerializer(serializers.Serializer):
    phone = serializers.CharField(validators=[validate_international_phonenumber])
    code = serializers.CharField()
    session = serializers.CharField()
