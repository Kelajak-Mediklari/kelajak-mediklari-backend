from django.contrib import admin

from apps.course.models import Course, Roadmap, Subject


@admin.register(Roadmap)
class RoadmapAdmin(admin.ModelAdmin):
    list_display = ("id", "image", "is_active")
    list_filter = ("is_active",)


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "is_active")
    search_fields = ("title", "slug")
    list_filter = ("is_active",)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "is_active")
    search_fields = ("title", "slug")
    list_filter = ("is_active", "is_unlimited", "is_main_course", "subject")
