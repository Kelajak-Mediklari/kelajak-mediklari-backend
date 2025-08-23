from rest_framework import generics
from rest_framework.response import Response

from apps.users.api_endpoints.auth.CheckPhone.serializers import CheckPhoneSerializer
from apps.users.models import User


class CheckPhoneView(generics.GenericAPIView):
    serializer_class = CheckPhoneSerializer

    def post(self, request, *args, **kwargs):
        """
        Check if a phone number exists in the system

        Required fields:
        - "phone": format E164 as like '+998945552233'
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data.get("phone")

        # Check if user exists with this phone number
        user_exists = User.objects.filter(phone=phone).exists()

        response_data = {"exists": user_exists, "phone": str(phone)}

        return Response(response_data)


__all__ = ["CheckPhoneView"]
