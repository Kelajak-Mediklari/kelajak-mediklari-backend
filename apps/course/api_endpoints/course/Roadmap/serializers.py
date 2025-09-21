from rest_framework import serializers

from apps.course.models import Roadmap


class RoadmapSerializer(serializers.ModelSerializer):
    subject = serializers.StringRelatedField(read_only=True)
    image = serializers.SerializerMethodField()

    class Meta:
        model = Roadmap
        fields = (
            "id",
            "image",
            "is_active",
            "subject",
        )

    def get_image(self, obj):
        if obj.image:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None
