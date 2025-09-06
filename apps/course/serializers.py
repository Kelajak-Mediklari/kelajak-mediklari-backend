from rest_framework import serializers

from apps.course.models import Subject


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ("id", "title", "slug", "icon")
