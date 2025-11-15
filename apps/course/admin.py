from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe

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
    list_display = ("title", "lesson", "type", "hls_progress_bar", "is_active")
    search_fields = ("title",)
    list_filter = ("is_active", "lesson", "type", "hls_processing_status")
    readonly_fields = ("hls_video_url", "hls_processing_status", "hls_progress_bar")

    fieldsets = (
        (
            "Basic Information",
            {"fields": ("lesson", "title", "content", "type", "order")},
        ),
        (
            "Video",
            {
                "fields": ("video", "hls_video_url", "hls_processing_status", "hls_progress_bar"),
                "description": "Upload a video file. It will be automatically converted to HLS format in the background.",
            },
        ),
        ("Test", {"fields": ("test",)}),
        ("Rewards", {"fields": ("award_coin", "award_point")}),
        (
            "Media & Files",
            {"fields": ("galleries", "attached_files"), "classes": ("collapse",)},
        ),
        ("Settings", {"fields": ("is_active",)}),
    )

    def hls_progress_bar(self, obj):
        """Display a visual progress bar for HLS processing status"""
        if not obj or not hasattr(obj, 'pk') or not obj.pk:
            return "-"
        
        status = obj.hls_processing_status or "pending"
        
        # Define status colors and percentages
        status_config = {
            "pending": {
                "percent": 0,
                "base_color": "#6c757d",  # Gray
                "stripe_color": "#8a9ba8",
                "bg_color": "#b0b0b0",
            },
            "processing": {
                "percent": 10,  # Start at first interval
                "base_color": "#0d6efd",  # Blue
                "stripe_color": "#4d8bfd",
                "bg_color": "#b0b0b0",
            },
            "completed": {
                "percent": 100,
                "base_color": "#99e666",  # Light green
                "stripe_color": "#b3ff80",
                "bg_color": "#b0b0b0",
            },
            "failed": {
                "percent": 100,
                "base_color": "#ff6b6b",  # Light red
                "stripe_color": "#ff8e8e",
                "bg_color": "#b0b0b0",
            },
        }
        
        config = status_config.get(status, status_config["pending"])
        
        # Get unique ID for this instance
        obj_id = str(obj.pk) if obj.pk else "default"
        
        # Determine border radius based on percentage
        if config["percent"] == 100:
            border_radius = "10px"
        else:
            border_radius = "10px 0 0 10px"
        
        # Create progress bar with diagonal stripes and gradient
        progress_html = format_html(
            """
            <div class="hls-progress-container" data-status="{status}" data-id="{id}">
                <style>
                    .hls-progress-wrapper-{id} {{
                        width: 200px;
                        height: 20px;
                        background: linear-gradient(to bottom, #d0d0d0 0%, #b0b0b0 100%);
                        border: 1px solid #888888;
                        border-radius: 10px;
                        overflow: hidden;
                        position: relative;
                        box-shadow: inset 0 1px 2px rgba(0,0,0,0.1);
                    }}
                    .hls-progress-bar-{id} {{
                        width: {percent}%;
                        height: 100%;
                        background-color: {base_color};
                        background-image: repeating-linear-gradient(
                            -45deg,
                            {base_color},
                            {base_color} 8px,
                            {stripe_color} 8px,
                            {stripe_color} 16px
                        );
                        border-radius: {border_radius};
                        position: relative;
                        transition: width 0.3s ease;
                        box-shadow: inset 0 1px 2px rgba(255,255,255,0.3);
                    }}
                    .hls-progress-bar-{id}::after {{
                        content: '';
                        position: absolute;
                        top: 0;
                        left: 0;
                        right: 0;
                        bottom: 0;
                        background: linear-gradient(to bottom, rgba(255,255,255,0.2) 0%, rgba(0,0,0,0.1) 100%);
                        border-radius: inherit;
                    }}
                </style>
                <div class="hls-progress-wrapper-{id}">
                    <div class="hls-progress-bar-{id}"></div>
                </div>
            </div>
            """,
            status=status,
            id=obj_id,
            percent=config["percent"],
            border_radius=border_radius,
            base_color=config["base_color"],
            stripe_color=config["stripe_color"],
            bg_color=config["bg_color"],
        )
        
        # Add animation script for processing status
        if status == "processing":
            # Use string replacement for JavaScript to avoid format_html issues
            animation_script = mark_safe(
                """
                <script>
                    (function() {
                        var progressBar = document.querySelector('.hls-progress-bar-""" + obj_id + """');
                        var container = document.querySelector('.hls-progress-container[data-status="processing"]');
                        
                        if (progressBar && container) {
                            // Progress intervals: 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95
                            var intervals = [10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95];
                            var currentIndex = 0;
                            
                            function updateProgress() {
                                if (currentIndex < intervals.length) {
                                    var percent = intervals[currentIndex];
                                    progressBar.style.width = percent + '%';
                                    
                                    // Update border radius if needed
                                    if (percent < 100) {
                                        progressBar.style.borderRadius = '10px 0 0 10px';
                                    } else {
                                        progressBar.style.borderRadius = '10px';
                                    }
                                    
                                    currentIndex++;
                                    
                                    // Continue animation or refresh if at end
                                    if (currentIndex < intervals.length) {
                                        setTimeout(updateProgress, 2000); // 2 seconds per interval
                                    } else {
                                        // Check status and refresh after reaching 95%
                                        setTimeout(function() {
                                            if (container && container.getAttribute('data-status') === 'processing') {
                                                location.reload();
                                            }
                                        }, 2000);
                                    }
                                }
                            }
                            
                            // Start from second interval (15%) since we start at 10%
                            currentIndex = 1;
                            // Start animation after a short delay
                            setTimeout(updateProgress, 2000);
                        }
                    })();
                </script>
                """
            )
            return mark_safe(str(progress_html) + str(animation_script))
        
        return progress_html
    
    hls_progress_bar.short_description = "HLS Processing Status"

    def get_readonly_fields(self, request, obj=None):
        """Make HLS fields readonly as they are auto-generated"""
        return self.readonly_fields


@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "slug",
        "questions_count",
        "test_duration",
        "type",
        "is_active",
    )
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
        "is_free_trial",
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
                    "finish_date",
                )
            },
        ),
        ("Rewards", {"fields": ("coins_earned", "points_earned")}),
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
                "fields": ("finish_date",),
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
