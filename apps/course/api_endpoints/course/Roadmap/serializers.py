from rest_framework import serializers

from apps.course.models import Roadmap


class RoadmapSerializer(serializers.ModelSerializer):
    subject = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Roadmap
        fields = (
            "id",
            "image",
            "is_active",
            "subject",
        )
