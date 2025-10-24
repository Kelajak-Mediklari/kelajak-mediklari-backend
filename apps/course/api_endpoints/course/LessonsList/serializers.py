from rest_framework import serializers

from apps.course.models import Lesson, UserCourse, UserLesson


class LessonsListSerializer(serializers.ModelSerializer):
    # parts_count is now provided by the queryset annotation
    parts_count = serializers.IntegerField(read_only=True)
    is_user_lesson_created = serializers.SerializerMethodField()
    progress_percent = serializers.SerializerMethodField()
    user_lesson_id = serializers.SerializerMethodField()
    user_course_id = serializers.SerializerMethodField()
    slug = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = (
            "id",
            "title",
            "slug",
            "order",
            "parts_count",
            "is_user_lesson_created",
            "user_lesson_id",
            "user_course_id",
            "progress_percent",
        )

    def get_is_user_lesson_created(self, obj):
        """Check if UserLesson exists for this lesson and the current user's course"""
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False

        # Use prefetched data if available (from queryset optimization)
        if hasattr(obj, "filtered_user_lessons"):
            return len(obj.filtered_user_lessons) > 0

        # Fallback for when prefetch is not available
        course_id = self.context.get("course_id")
        if not course_id:
            return False

        return UserLesson.objects.filter(
            lesson=obj, user_course__user=request.user, user_course__course_id=course_id
        ).exists()

    def get_progress_percent(self, obj):
        """Get progress percentage from UserLesson if it exists"""
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return 0.00

        # Use prefetched data if available (from queryset optimization)
        if hasattr(obj, "filtered_user_lessons") and obj.filtered_user_lessons:
            return float(obj.filtered_user_lessons[0].progress_percent)

        # Fallback for when prefetch is not available
        course_id = self.context.get("course_id")
        if not course_id:
            return 0.00

        user_lesson = UserLesson.objects.filter(
            lesson=obj, user_course__user=request.user, user_course__course_id=course_id
        ).first()

        return float(user_lesson.progress_percent) if user_lesson else 0.00

    def get_user_lesson_id(self, obj):
        """Get UserLesson ID if it exists for this lesson and the current user's course"""
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return None

        # Use prefetched data if available (from queryset optimization)
        if hasattr(obj, "filtered_user_lessons") and obj.filtered_user_lessons:
            return obj.filtered_user_lessons[0].id

        # Fallback for when prefetch is not available
        course_id = self.context.get("course_id")
        if not course_id:
            return None

        user_lesson = UserLesson.objects.filter(
            lesson=obj, user_course__user=request.user, user_course__course_id=course_id
        ).first()

        return user_lesson.id if user_lesson else None

    def get_user_course_id(self, obj):
        """Get UserCourse ID if user has access to the course (regardless of UserLesson existence)"""
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return None

        # Get user_course from context (added in view)
        user_course = self.context.get("user_course")
        if user_course:
            return user_course.id

        # Fallback for when context is not available
        course_id = self.context.get("course_id")
        if not course_id:
            return None

        try:
            user_course = UserCourse.objects.get(user=request.user, course_id=course_id)
            return user_course.id
        except UserCourse.DoesNotExist:
            return None

    def get_slug(self, obj):
        """Return slug only for first 3 lessons if user hasn't bought the course"""
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return None

        # Check if user has purchased the course
        user_course = self.context.get("user_course")
        if user_course:
            # User has purchased the course, return the actual slug
            return obj.slug

        # User hasn't purchased the course, check if this is one of the first 3 lessons
        course_id = self.context.get("course_id")
        if not course_id:
            return None

        # Get the first 3 lessons of the course ordered by id
        first_three_lessons = Lesson.objects.filter(
            course_id=course_id, 
            is_active=True
        ).order_by('id')[:3]

        # Check if current lesson is in the first 3
        if obj in first_three_lessons:
            return obj.slug
        else:
            return None
