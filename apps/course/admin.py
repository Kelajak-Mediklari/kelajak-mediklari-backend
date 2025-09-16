from django.contrib import admin

from apps.course.models import (
    AnswerChoice,
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
    UserAnswer,
    UserCourse,
    UserLesson,
    UserLessonPart,
    UserTest,
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
    prepopulated_fields = {"slug": ("title",)}


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "is_active")
    search_fields = ("title", "slug")
    list_filter = ("is_active", "is_unlimited", "is_main_course", "subject")
    prepopulated_fields = {"slug": ("title",)}


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


@admin.register(AnswerChoice)
class AnswerChoiceAdmin(admin.ModelAdmin):
    list_display = ("choice_text", "choice_label", "question", "order")
    search_fields = ("choice_text", "choice_label", "question")
    list_filter = ("question", "order")


# User Progress Tracking Admin Classes


@admin.register(UserCourse)
class UserCourseAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "course",
        "progress_percent",
        "is_completed",
        "start_date",
        "finish_date",
    )
    search_fields = ("user__phone", "user__full_name", "course__title")
    list_filter = ("is_completed", "course", "start_date", "finish_date")
    readonly_fields = (
        "progress_percent",
        "coins_earned",
        "points_earned",
    )
    date_hierarchy = "start_date"

    fieldsets = (
        ("Basic Information", {"fields": ("user", "course")}),
        (
            "Progress",
            {
                "fields": (
                    "progress_percent",
                    "is_completed",
                    "start_date",
                    "finish_date",
                )
            },
        ),
        ("Rewards", {"fields": ("coins_earned", "points_earned")}),
        (
            "Timestamps",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    def get_readonly_fields(self, request, obj=None):
        readonly = list(self.readonly_fields)
        if obj:  # editing an existing object
            readonly.extend(["user", "course"])
        return readonly


@admin.register(UserLesson)
class UserLessonAdmin(admin.ModelAdmin):
    list_display = (
        "user_course",
        "lesson",
        "progress_percent",
        "is_completed",
        "start_date",
        "completion_date",
    )
    search_fields = (
        "user_course__user__phone",
        "user_course__user__full_name",
        "lesson__title",
    )
    list_filter = ("is_completed", "lesson__course", "start_date", "completion_date")
    readonly_fields = ("progress_percent",)
    date_hierarchy = "start_date"

    def get_readonly_fields(self, request, obj=None):
        readonly = list(self.readonly_fields)
        if obj:  # editing an existing object
            readonly.extend(["user_course", "lesson"])
        return readonly


@admin.register(UserLessonPart)
class UserLessonPartAdmin(admin.ModelAdmin):
    list_display = (
        "user_lesson",
        "lesson_part",
        "is_completed",
        "start_date",
        "completion_date",
    )
    search_fields = ("user_lesson__user_course__user__phone", "lesson_part__title")
    list_filter = ("is_completed", "lesson_part__type", "start_date", "completion_date")
    date_hierarchy = "start_date"

    def get_readonly_fields(self, request, obj=None):
        readonly = list(self.readonly_fields)
        if obj:  # editing an existing object
            readonly.extend(["user_lesson", "lesson_part"])
        return readonly


@admin.register(UserTest)
class UserTestAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "test",
        "is_passed",
        "attempt_number",
        "is_submitted",
        "start_date",
        "finish_date",
    )
    search_fields = ("user__phone", "user__full_name", "test__title")
    list_filter = (
        "is_passed",
        "is_submitted",
        "is_in_progress",
        "test__type",
        "start_date",
        "finish_date",
    )
    readonly_fields = ("total_questions", "correct_answers")
    date_hierarchy = "start_date"

    fieldsets = (
        ("Basic Information", {"fields": ("user", "test", "attempt_number")}),
        ("Status", {"fields": ("is_submitted", "is_in_progress", "is_passed")}),
        ("Results", {"fields": ("total_questions", "correct_answers")}),
        (
            "Timestamps",
            {
                "fields": ("start_date", "finish_date", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    def get_readonly_fields(self, request, obj=None):
        readonly = list(self.readonly_fields)
        if obj:  # editing an existing object
            readonly.extend(["user", "test"])
        return readonly


@admin.register(UserAnswer)
class UserAnswerAdmin(admin.ModelAdmin):
    list_display = ("user_test", "question", "is_correct", "answered_at")
    search_fields = (
        "user_test__user__phone",
        "user_test__user__full_name",
        "question__question_text",
    )
    list_filter = ("is_correct", "user_test__test", "answered_at")
    readonly_fields = ("is_correct",)
    date_hierarchy = "answered_at"

    fieldsets = (
        ("Basic Information", {"fields": ("user_test", "question")}),
        (
            "Answer",
            {
                "fields": (
                    "selected_choice",
                    "boolean_answer",
                    "text_answer",
                    "matching_answer",
                    "book_answer",
                )
            },
        ),
        ("Result", {"fields": ("is_correct", "answered_at")}),
    )

    def get_readonly_fields(self, request, obj=None):
        readonly = list(self.readonly_fields)
        if obj:  # editing an existing object
            readonly.extend(["user_test", "question"])
        return readonly
