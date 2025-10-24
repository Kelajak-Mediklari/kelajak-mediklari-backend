from datetime import datetime, timedelta
from django.db.models.signals import post_save
from django.dispatch import receiver
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
    """
    if created and instance.is_active:
        group = instance.group
        teacher = group.teacher
        course = group.course

        try:
            teacher_limit = TeacherGlobalLimit.objects.get(
                teacher=teacher,
                course=course
            )
            # Increment used count
            teacher_limit.used += 1
            # Update remaining count
            teacher_limit.remaining = teacher_limit.limit - teacher_limit.used
            teacher_limit.save(update_fields=['used', 'remaining'])
        except TeacherGlobalLimit.DoesNotExist:
            pass  # Handle case where limit doesn't exist
