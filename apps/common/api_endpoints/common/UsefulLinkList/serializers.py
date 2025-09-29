from rest_framework import serializers
from django.conf import settings
from apps.common.models import UsefulLink
from apps.common.api_endpoints.common.file_serializers import AttachedFileSerializer


class UsefulLinkListSerializer(serializers.ModelSerializer):
    category_title = serializers.CharField(source='category.title', read_only=True)
    category_slug = serializers.CharField(source='category.slug', read_only=True)
    subject_title = serializers.CharField(source='subject.title', read_only=True)
    subject_slug = serializers.CharField(source='subject.slug', read_only=True)
    cover_image = serializers.SerializerMethodField()
    video_file = serializers.SerializerMethodField()
    files = serializers.SerializerMethodField()

    class Meta:
        model = UsefulLink
        fields = [
            'id', 'title', 'slug', 'description', 
            'category_title', 'category_slug', 'subject_title', 'subject_slug',
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
    
    def get_files(self, obj):
        serializer = AttachedFileSerializer(context=self.context)
        return [serializer.to_representation(f) for f in obj.files.all() if f.file]