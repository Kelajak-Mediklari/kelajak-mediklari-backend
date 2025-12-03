from datetime import datetime, timedelta
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from apps.course.models import UserCourse
from apps.users.models import Group, GroupMember, TeacherGlobalLimit


@receiver(post_save, sender=Group)
def calculate_group_end_date(sender, instance, created, **kwargs):
    """
    Calculate and set group end_date based on course duration_months
    """
    if created and instance.course and instance.course.duration_months:
        start_date = datetime.now().date()
        end_date = start_date + timedelta(days=instance.course.duration_months * 30)
        instance.group_end_date = end_date
        instance.save(update_fields=['group_end_date'])


@receiver(post_save, sender=GroupMember)
def update_teacher_global_limit(sender, instance, created, **kwargs):
    """
    Update teacher global limit when a group member is added
    Check if teacher has remaining limit before proceeding
    Only assign teacher and create UserCourse if limit is available
    """
    if created and instance.is_active:
        group = instance.group
        teacher = group.teacher
        course = group.course

        if not teacher or not course:
            return

        try:
            teacher_limit = TeacherGlobalLimit.objects.get(
                teacher=teacher,
                course=course
            )

            # Check if teacher has remaining limit BEFORE creating UserCourse and assigning teacher
            if teacher_limit.remaining <= 0:
                # No remaining limit - inform user but keep GroupMember
                # Don't create UserCourse or assign teacher
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(
                    f"GroupMember created but limit exceeded: Teacher {teacher.full_name} (ID: {teacher.id}) "
                    f"has reached the limit ({teacher_limit.limit}) for course {course.title} (ID: {course.id}). "
                    f"Remaining: {teacher_limit.remaining}. UserCourse not created and teacher not assigned."
                )
                # Keep GroupMember but don't proceed with UserCourse creation or teacher assignment
                return

            # Teacher has remaining limit - proceed with creation
            # Create student course FIRST
            UserCourse.objects.get_or_create(
                user=instance.user,
                course=course,
                defaults={
                    'finish_date': group.group_end_date,
                }
            )

            # Assign teacher AFTER successful UserCourse creation
            if not instance.user.teacher:
                instance.user.teacher = teacher
                instance.user.save(update_fields=['teacher'])

            # Increment used count AFTER successful creation
            teacher_limit.used += 1
            # Update remaining count
            teacher_limit.remaining = teacher_limit.limit - teacher_limit.used
            teacher_limit.save(update_fields=['used', 'remaining'])

        except TeacherGlobalLimit.DoesNotExist:
            # If limit doesn't exist, inform user but keep GroupMember
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(
                f"GroupMember created but no limit set: Teacher {teacher.full_name} (ID: {teacher.id}) "
                f"does not have a limit set for course {course.title} (ID: {course.id}). "
                "UserCourse not created and teacher not assigned. Please set up the teacher's global limit first."
            )
            # Keep GroupMember but don't proceed with UserCourse creation or teacher assignment
            return


@receiver(post_delete, sender=Group)
def delete_group_members(sender, instance, **kwargs):
    """
    Delete group members when a group is deleted
    """
    GroupMember.objects.filter(group=instance).delete()


@receiver(post_delete, sender=GroupMember)
def delete_user_course(sender, instance, **kwargs):
    """
    Delete user course and update teacher global limit when a group member is deleted
    """
    group = instance.group
    teacher = group.teacher if group else None
    course = group.course if group else None

    if not group or not teacher or not course:
        return

    # Delete user course
    UserCourse.objects.filter(user=instance.user, course=course, is_expired=False).delete()

    # Decrement group's current_member_count if it was active
    if instance.is_active and group.current_member_count > 0:
        group.current_member_count -= 1
        group.save(update_fields=['current_member_count'])

    # Update teacher global limit - decrement used and increment remaining
    try:
        teacher_limit = TeacherGlobalLimit.objects.get(
            teacher=teacher,
            course=course
        )
        if teacher_limit.used > 0:
            teacher_limit.used -= 1
            teacher_limit.remaining = teacher_limit.limit - teacher_limit.used
            teacher_limit.save(update_fields=['used', 'remaining'])
    except TeacherGlobalLimit.DoesNotExist:
        pass  # Handle case where limit doesn't exist
