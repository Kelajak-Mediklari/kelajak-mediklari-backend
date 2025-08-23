from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated

from .serializers import ProfileGetSerializer


class ProfileGetView(RetrieveAPIView):
    serializer_class = ProfileGetSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


__all__ = ["ProfileGetView"]
