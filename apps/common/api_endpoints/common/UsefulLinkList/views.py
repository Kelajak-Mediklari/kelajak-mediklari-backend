from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny
from rest_framework import filters

from apps.common.models import UsefulLink
from apps.common.api_endpoints.common.UsefulLinkList.serializers import UsefulLinkListSerializer


class UsefulLinkListAPIView(ListAPIView):
    """
    API endpoint to list all active useful links with filters
    """
    serializer_class = UsefulLinkListSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'category__title', 'subject__title']
    ordering_fields = ['created_at', 'updated_at', 'title']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Return only active useful links"""
        return UsefulLink.objects.filter(is_active=True).select_related('category', 'subject').prefetch_related('files')
