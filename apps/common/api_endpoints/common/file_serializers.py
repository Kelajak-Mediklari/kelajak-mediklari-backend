from rest_framework import serializers
from django.conf import settings
from django.core.files.storage import default_storage
import os


def get_file_type(file_name):
    """Infer file type from extension (lowercased)."""
    if not file_name:
        return None

    ext = os.path.splitext(file_name)[1].lower()
    type_mapping = {
        ".pdf": "pdf",
        ".doc": "doc",
        ".docx": "doc",
        ".txt": "txt",
        ".rtf": "rtf",
        ".jpg": "image",
        ".jpeg": "image",
        ".png": "image",
        ".gif": "image",
        ".bmp": "image",
        ".svg": "image",
        ".mp4": "video",
        ".avi": "video",
        ".mov": "video",
        ".wmv": "video",
        ".flv": "video",
        ".mp3": "audio",
        ".wav": "audio",
        ".ogg": "audio",
        ".zip": "archive",
        ".rar": "archive",
        ".7z": "archive",
        ".xlsx": "excel",
        ".xls": "excel",
        ".pptx": "presentation",
        ".ppt": "presentation",
    }
    return type_mapping.get(ext, "unknown")


def get_file_type_display(file_type):
    """Human-readable file type."""
    type_display_mapping = {
        "pdf": "PDF",
        "doc": "Word Document",
        "txt": "Text File",
        "rtf": "Rich Text Format",
        "image": "Image",
        "video": "Video",
        "audio": "Audio",
        "archive": "Archive",
        "excel": "Excel Spreadsheet",
        "presentation": "Presentation",
        "unknown": "Unknown File Type",
    }
    return type_display_mapping.get(file_type, "Unknown File Type")


def format_file_size(size_bytes):
    """Convert bytes to human readable format like '143 KB'."""
    if not size_bytes:
        return "0 B"

    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    size = float(size_bytes)
    while size >= 1024 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1
    return f"{size:.0f} {size_names[i]}"


class AttachedFileSerializer(serializers.Serializer):
    """
    Reusable serializer for any model instance with a `file` attribute or a FileField itself.

    Produces schema:
    {
      id, file, file_type, file_type_display, size, size_display, file_name
    }
    """

    def _represent_from_fieldfile(self, field_file):
        request = self.context.get("request")

        if request:
            file_url = request.build_absolute_uri(field_file.url)
        else:
            file_url = f"{settings.MEDIA_URL}{field_file.name}"

        file_name = os.path.basename(field_file.name) if field_file.name else None
        file_type = get_file_type(file_name)
        file_type_display = get_file_type_display(file_type)

        try:
            size = field_file.size if getattr(field_file, "size", None) else (
                default_storage.size(field_file.name) if field_file.name else 0
            )
        except (OSError, ValueError):
            size = 0

        return {
            "file": file_url,
            "file_type": file_type,
            "file_type_display": file_type_display,
            "size": size,
            "size_display": format_file_size(size),
            "file_name": file_name,
        }

    def to_representation(self, instance):
        # If a model instance with `.file`, include its id and derive from its file field
        if hasattr(instance, "file") and instance.file:
            base = self._represent_from_fieldfile(instance.file)
            base["id"] = getattr(instance, "id", None)
            return base

        # If the instance is a raw FieldFile
        if hasattr(instance, "url") and hasattr(instance, "name"):
            base = self._represent_from_fieldfile(instance)
            base["id"] = None
            return base

        return None


