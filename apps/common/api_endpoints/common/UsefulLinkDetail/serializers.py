from rest_framework import serializers
from django.conf import settings
from apps.common.models import UsefulLink, UsefulLinkCategory, UsefulLinkSubject, UsefulLinkFile


class UsefulLinkFileSerializer(serializers.ModelSerializer):
    file = serializers.SerializerMethodField()

    class Meta:
        model = UsefulLinkFile
        fields = ['id', 'file', 'is_active', 'created_at', 'updated_at']

    def get_file(self, obj):
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
            return f"{settings.MEDIA_URL}{obj.file.name}"
        return None


class UsefulLinkCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = UsefulLinkCategory
        fields = ['id', 'title', 'slug', 'created_at', 'updated_at']


class UsefulLinkSubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsefulLinkSubject
        fields = ['id', 'title', 'slug', 'created_at', 'updated_at']


class UsefulLinkDetailSerializer(serializers.ModelSerializer):
    category = UsefulLinkCategorySerializer(read_only=True)
    subject = UsefulLinkSubjectSerializer(read_only=True)
    files = UsefulLinkFileSerializer(many=True, read_only=True)
    cover_image = serializers.SerializerMethodField()
    video_file = serializers.SerializerMethodField()

    class Meta:
        model = UsefulLink
        fields = [
            'id', 'title', 'slug', 'description', 'category', 'subject',
            'cover_image', 'video_url', 'video_file', 'is_active', 'files',
            'created_at', 'updated_at'
        ]

    def get_cover_image(self, obj):
        if obj.cover_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.cover_image.url)
            return f"{settings.MEDIA_URL}{obj.cover_image.name}"
        return None

    def get_video_file(self, obj):
        if obj.video_file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.video_file.url)
            return f"{settings.MEDIA_URL}{obj.video_file.name}"
        return None
