from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404

from apps.common.models import UsefulLink
from apps.common.api_endpoints.common.UsefulLinkDetail.serializers import UsefulLinkDetailSerializer


class UsefulLinkDetailAPIView(RetrieveAPIView):
    """
    API endpoint to get useful link details
    """
    serializer_class = UsefulLinkDetailSerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'

    def get_queryset(self):
        """Return only active useful links"""
        return UsefulLink.objects.filter(is_active=True).select_related('category', 'subject').prefetch_related('files')
