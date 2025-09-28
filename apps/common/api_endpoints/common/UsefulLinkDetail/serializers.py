from rest_framework import serializers
from django.conf import settings
from django.core.files.storage import default_storage
import os
from apps.common.models import UsefulLink, UsefulLinkCategory, UsefulLinkSubject, UsefulLinkFile


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


class FileSerializer(serializers.Serializer):
    """Reusable file serializer with comprehensive metadata"""
    
    def to_representation(self, file_field):
        if not file_field:
            return None
        
        request = self.context.get('request')
        
        # Get file URL
        if request:
            file_url = request.build_absolute_uri(file_field.url)
        else:
            file_url = f"{settings.MEDIA_URL}{file_field.name}"
        
        # Get file metadata
        file_name = os.path.basename(file_field.name) if file_field.name else None
        file_type = get_file_type(file_name)
        file_type_display = get_file_type_display(file_type)
        
        # Get file size
        try:
            if hasattr(file_field, 'size') and file_field.size:
                size = file_field.size
            else:
                # Try to get size from storage
                size = default_storage.size(file_field.name) if file_field.name else 0
        except (OSError, ValueError):
            size = 0
        
        size_display = format_file_size(size)
        
        return {
            'file_url': file_url,
            'file_type': file_type,
            'file_type_display': file_type_display,
            'size': size,
            'size_display': size_display,
            'file_name': file_name,
        }


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
