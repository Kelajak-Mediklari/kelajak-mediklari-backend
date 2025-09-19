from rest_framework import serializers
from apps.common.models import District


class DistrictSerializer(serializers.ModelSerializer):
    region_name = serializers.CharField(source='region.name', read_only=True)
    
    class Meta:
        model = District
        fields = ['id', 'name', 'region', 'region_name', 'created_at', 'updated_at']
