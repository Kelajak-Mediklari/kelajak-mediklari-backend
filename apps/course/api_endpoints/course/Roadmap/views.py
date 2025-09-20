from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.course.models import Roadmap, Subject

from .serializers import RoadmapSerializer


class RoadmapAPIView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, subject_id, *args, **kwargs):
        # First verify the subject exists
        subject = get_object_or_404(Subject, id=subject_id, is_active=True)

        # Get the roadmap for this subject
        roadmap = get_object_or_404(Roadmap, subject=subject, is_active=True)

        serializer = RoadmapSerializer(roadmap)
        return Response(serializer.data)


__all__ = ["RoadmapAPIView"]
