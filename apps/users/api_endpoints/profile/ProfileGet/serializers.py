from rest_framework import serializers

from apps.users.models import User


class TeacherShortInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "full_name",
            "username",
            "phone",
            "avatar",
        ]


class ProfileGetSerializer(serializers.ModelSerializer):
    region_name = serializers.CharField(source='region.name', read_only=True)
    district_name = serializers.CharField(source='district.name', read_only=True)
    is_selected_by_teacher = serializers.SerializerMethodField(read_only=True)
    teacher = TeacherShortInfoSerializer(read_only=True)
    group_names = serializers.SerializerMethodField(read_only=True)


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
            "gender",
            "coin",
            "point",
            "is_selected_by_teacher",
            "teacher",
            "group_names"
        ]

    def get_is_selected_by_teacher(self, obj):
        return obj.is_selected_by_teacher
    
    def get_group_names(self, obj):
        # Get all active group names for this user
        group_members = obj.group_members.filter(is_active=True).select_related('group')
        return [group_member.group.name for group_member in group_members]
    
