from rest_framework import serializers
from django.conf import settings
from apps.common.models import UsefulLink


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
        files_data = []
        for file_obj in obj.files.all():
            if file_obj.file:
                request = self.context.get('request')
                if request:
                    file_url = request.build_absolute_uri(file_obj.file.url)
                else:
                    file_url = f"{settings.MEDIA_URL}{file_obj.file.name}"
                
                files_data.append({
                    'id': file_obj.id,
                    'file': file_url,
                    'is_active': file_obj.is_active,
                    'created_at': file_obj.created_at,
                    'updated_at': file_obj.updated_at
                })
        return files_data