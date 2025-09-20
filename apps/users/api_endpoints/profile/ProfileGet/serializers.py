from rest_framework import serializers

from apps.users.models import User


class ProfileGetSerializer(serializers.ModelSerializer):
    region_name = serializers.CharField(source='region.name', read_only=True)
    district_name = serializers.CharField(source='district.name', read_only=True)
    
    class Meta:
        model = User
        fields = [
            "id", 
            "full_name", 
            "username", 
            "phone",
            "email",
            "avatar",
            "grade",
            "birth_date",
            "region",
            "region_name",
            "district", 
            "district_name",
            "address_index",
            "gender"
        ]
