from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.utils.translation import gettext_lazy as _
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.services import CacheTypes, generate_cache_key

from .serializers import UserChangePhoneSerializer

User = get_user_model()


class UserChangePhoneAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(request_body=UserChangePhoneSerializer)
    def post(self, request, *args, **kwargs):
        """
        "code": code from sms which you received
        "session": session key for sms code,  you must get from `users/SendCodeForChangePhone/` api
        "phone": format E164 as like '+998945552233'
        """
        serializer = UserChangePhoneSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data.get("phone")
        self.check_user_exists(phone)

        code = serializer.validated_data.get("code")
        session = serializer.validated_data.get("session")

        cache_key = generate_cache_key(CacheTypes.change_phone_sms_code, phone, session)

        if not self.is_code_valid(cache_key, code):
            raise ValidationError(detail={"code": _("Wrong code!")}, code="invalid")

        user = User.objects.get(id=request.user.id)
        user.phone = phone
        user.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @staticmethod
    def check_user_exists(phone):
        if User.objects.filter(phone=phone):
            raise ValidationError(
                detail={"phone": _("User with this phone already exists!")},
                code="unique",
            )

    @staticmethod
    def is_code_valid(cache_key, code):
        valid_code = cache.get(cache_key)
        if valid_code != code:
            return False
        return True


__all__ = ["UserChangePhoneAPIView"]
