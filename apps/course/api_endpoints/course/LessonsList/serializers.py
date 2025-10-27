from rest_framework import serializers

from apps.course.models import Lesson, UserCourse, UserLesson
from apps.users.models import GroupMember, GroupMemberGrade


class LessonsListSerializer(serializers.ModelSerializer):
    # parts_count is now provided by the queryset annotation
    parts_count = serializers.IntegerField(read_only=True)
    is_user_lesson_created = serializers.SerializerMethodField()
    progress_percent = serializers.SerializerMethodField()
    user_lesson_id = serializers.SerializerMethodField()
    user_course_id = serializers.SerializerMethodField()
    slug = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

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
            "status",
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

    def get_status(self, obj):
        """Return status based on lesson completion for group members"""
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return None

        course_id = self.context.get("course_id")
        if not course_id:
            return None

        # Check if user is a group member for this course
        group_member = self.context.get("group_member")
        if not group_member:
            return None

        # For group members, check lesson status based on completion
        return self._check_lesson_status_for_group_member(obj, group_member, course_id)

    def _check_lesson_status_for_group_member(self, lesson, group_member, course_id):
        """Check lesson status for group member based on completion pattern"""
        # First lesson is always open
        if lesson.order == 1:
            return "open"
        
        # Get all lessons ordered by their order
        all_lessons = Lesson.objects.filter(
            course_id=course_id,
            is_active=True
        ).order_by('order')
        
        # Find the current lesson's position
        current_position = lesson.order
        
        # Check completed lessons (lessons with passing grades)
        completed_lessons = []
        for check_lesson in all_lessons:
            if check_lesson.order < current_position:
                try:
                    grade = GroupMemberGrade.objects.get(
                        group_member=group_member,
                        lesson=check_lesson
                    )
                    
                    # Check if both theoretical and practical grades meet passing requirements
                    theoretical_passed = grade.theoretical_ball >= check_lesson.theoretical_pass_ball
                    practical_passed = grade.practical_ball >= check_lesson.practical_pass_ball
                    
                    if theoretical_passed and practical_passed:
                        completed_lessons.append(check_lesson.order)
                        
                except GroupMemberGrade.DoesNotExist:
                    pass
        
        # Determine status based on completion pattern
        if not completed_lessons:
            # No lessons completed yet
            if current_position <= 3:
                return "lock"  # First 3 lessons are "lock" by default
            else:
                return "loock"  # Beyond first 3 are "loock"
        else:
            # Some lessons are completed
            max_completed = max(completed_lessons)
            
            # If current lesson is within the next 2 lessons after the last completed lesson
            if current_position <= max_completed + 2:
                return "lock"
            else:
                return "loock"
