from django.contrib import admin

from . import models


@admin.register(models.VersionHistory)
class VersionHistoryAdmin(admin.ModelAdmin):
    list_display = ("id", "version", "required", "created_at", "updated_at")
    list_display_links = ("id", "version")
    list_filter = ("required", "created_at", "updated_at")
    search_fields = ("version",)


@admin.register(models.FrontendTranslation)
class FrontTranslationAdmin(admin.ModelAdmin):
    list_display = ("id", "key", "text", "created_at", "updated_at")
    list_display_links = ("id", "key")
    list_filter = ("created_at", "updated_at")
    search_fields = ("key", "version")


@admin.register(models.UsefulLinkCategory)
class UsefulLinkCategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "slug", "created_at", "updated_at")
    list_display_links = ("id", "title")
    list_filter = ("created_at", "updated_at")
    search_fields = ("title", "slug")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(models.UsefulLinkSubject)
class UsefulLinkSubjectAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "slug", "created_at", "updated_at")
    list_display_links = ("id", "title")
    list_filter = ("created_at", "updated_at")
    search_fields = ("title", "slug")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(models.UsefulLinkFile)
class UsefulLinkFileAdmin(admin.ModelAdmin):
    list_display = ("id", "file", "is_active", "created_at", "updated_at")
    list_display_links = ("id", "file")
    list_filter = ("is_active", "created_at", "updated_at")
    search_fields = ("file",)


@admin.register(models.UsefulLink)
class UsefulLinkAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "slug", "category", "subject", "is_active", "created_at", "updated_at")
    list_display_links = ("id", "title")
    list_filter = ("category", "subject", "is_active", "created_at", "updated_at")
    search_fields = ("title", "slug", "description")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("files",)
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'description', 'is_active')
        }),
        ('Relations', {
            'fields': ('category', 'subject')
        }),
        ('Media', {
            'fields': ('cover_image', 'video_url', 'video_file', 'files')
        }),
    )
