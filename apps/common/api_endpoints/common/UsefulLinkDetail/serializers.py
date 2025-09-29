from rest_framework import serializers
from django.conf import settings
from django.core.files.storage import default_storage
import os
from apps.common.models import UsefulLink, UsefulLinkCategory, UsefulLinkSubject, UsefulLinkFile
from apps.common.api_endpoints.common.file_serializers import (
    AttachedFileSerializer,
)


def get_file_type(file_name):
    """Get file type from file extension"""
    if not file_name:
        return None
    
    ext = os.path.splitext(file_name)[1].lower()
    type_mapping = {
        '.pdf': 'pdf',
        '.doc': 'doc',
        '.docx': 'doc',
        '.txt': 'txt',
        '.rtf': 'rtf',
        '.jpg': 'image',
        '.jpeg': 'image',
        '.png': 'image',
        '.gif': 'image',
        '.bmp': 'image',
        '.svg': 'image',
        '.mp4': 'video',
        '.avi': 'video',
        '.mov': 'video',
        '.wmv': 'video',
        '.flv': 'video',
        '.mp3': 'audio',
        '.wav': 'audio',
        '.ogg': 'audio',
        '.zip': 'archive',
        '.rar': 'archive',
        '.7z': 'archive',
        '.xlsx': 'excel',
        '.xls': 'excel',
        '.pptx': 'presentation',
        '.ppt': 'presentation',
    }
    return type_mapping.get(ext, 'unknown')


def get_file_type_display(file_type):
    """Get human-readable file type display"""
    type_display_mapping = {
        'pdf': 'PDF',
        'doc': 'Word Document',
        'txt': 'Text File',
        'rtf': 'Rich Text Format',
        'image': 'Image',
        'video': 'Video',
        'audio': 'Audio',
        'archive': 'Archive',
        'excel': 'Excel Spreadsheet',
        'presentation': 'Presentation',
        'unknown': 'Unknown File Type'
    }
    return type_display_mapping.get(file_type, 'Unknown File Type')


def format_file_size(size_bytes):
    """Convert bytes to human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.0f} {size_names[i]}"


class FileSerializer(AttachedFileSerializer):
    pass


class UsefulLinkFileSerializer(serializers.ModelSerializer):
    file = FileSerializer(read_only=True)

    class Meta:
        model = UsefulLinkFile
        fields = ['id', 'file', 'is_active', 'created_at', 'updated_at']


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
