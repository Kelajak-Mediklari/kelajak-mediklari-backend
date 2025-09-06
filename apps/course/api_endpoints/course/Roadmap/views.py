from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.course.models import Roadmap

from .serializers import RoadmapSerializer


class RoadmapAPIView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        roadmap = Roadmap.objects.filter(is_active=True).first()
        if not roadmap:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = RoadmapSerializer(roadmap)
        return Response(serializer.data)


__all__ = ["RoadmapAPIView"]
