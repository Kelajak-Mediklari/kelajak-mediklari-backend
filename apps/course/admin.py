from django.contrib import admin

from apps.course.models import (
    Course,
    File,
    Gallery,
    Lesson,
    LessonPart,
    MatchingPair,
    Question,
    Roadmap,
    Subject,
    Test,
)


@admin.register(Gallery)
class GalleryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "image",
    )


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "file",
    )


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


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "is_active")
    search_fields = ("title", "slug")
    list_filter = ("is_active", "course")


@admin.register(LessonPart)
class LessonPartAdmin(admin.ModelAdmin):
    list_display = ("title", "lesson", "type", "is_active")
    search_fields = ("title",)
    list_filter = ("is_active", "lesson", "type")


@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "is_active")
    search_fields = ("title", "slug")
    list_filter = ("is_active", "type")


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("question_text", "test", "is_active")
    search_fields = ("question_text",)
    list_filter = ("is_active", "test")


@admin.register(MatchingPair)
class MatchingPairAdmin(admin.ModelAdmin):
    list_display = ("left_item", "right_item", "question", "order")
    search_fields = ("left_item", "right_item", "question")
    list_filter = ("question", "order")
