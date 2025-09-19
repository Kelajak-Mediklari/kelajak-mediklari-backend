from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from apps.common.models import Region
from apps.common.api_endpoints.common.RegionList.serializers import RegionSerializer


class RegionListAPIView(ListAPIView):
    """
    API endpoint to get list of all regions
    """
    queryset = Region.objects.all()
    serializer_class = RegionSerializer

    def get(self, request, *args, **kwargs):
        regions = self.get_queryset()
        serializer = self.get_serializer(regions, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data,
            'count': regions.count()
        }, status=status.HTTP_200_OK)
