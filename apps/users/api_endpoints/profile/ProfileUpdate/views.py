from rest_framework.generics import UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser

from .serializers import ProfileUpdateSerializer


class ProfileUpdateView(UpdateAPIView):
    serializer_class = ProfileUpdateSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]


    def get_object(self):
        return self.request.user


__all__ = ["ProfileUpdateView"]
