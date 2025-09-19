from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from apps.common.models import District, Region
from apps.common.api_endpoints.common.DistrictList.serializers import DistrictSerializer


class DistrictListAPIView(ListAPIView):
    """
    API endpoint to get list of districts by region
    """
    serializer_class = DistrictSerializer

    def get_queryset(self):
        region_id = self.request.query_params.get('region_id')
        if region_id:
            region = get_object_or_404(Region, id=region_id)
            return District.objects.select_related('region').filter(region=region)
        return District.objects.select_related('region').all()

    def get(self, request, *args, **kwargs):
        districts = self.get_queryset()
        serializer = self.get_serializer(districts, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data,
            'count': districts.count()
        }, status=status.HTTP_200_OK)
