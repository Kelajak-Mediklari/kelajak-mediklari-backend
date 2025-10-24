from rest_framework import serializers

from apps.users.models import Group


class GroupListSerializer(serializers.ModelSerializer):
    members_count = serializers.IntegerField(read_only=True)
    subject = serializers.CharField(source='course.subject.title', read_only=True)
    course_name = serializers.CharField(source='course.title', read_only=True)
    end_date = serializers.DateField(source='group_end_date', read_only=True)
    
    class Meta:
        model = Group
        fields = [
            'id',
            'name',
            'members_count',
            'subject',
            'course_name',
            'end_date',
        ]
