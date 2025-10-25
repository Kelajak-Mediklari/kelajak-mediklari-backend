from datetime import date
from celery import shared_task
from django.utils.translation import gettext_lazy as _

from apps.users.models import Group, GroupMember
from apps.course.models import UserCourse


@shared_task
def check_expired_groups():
    """
    Celery task to check for expired groups and update their status.
    Runs daily to mark expired groups and their members as inactive.
    """
    today = date.today()
    
    # Find groups that have expired (group_end_date <= today and is_active=True)
    expired_groups = Group.objects.filter(
        group_end_date__lte=today,
        is_active=True
    )
    
    expired_count = 0
    expired_members_count = 0
    expired_user_courses_count = 0
    
    for group in expired_groups:
        # Mark group as inactive
        group.is_active = False
        group.save(update_fields=['is_active'])
        expired_count += 1
        
        # Get all active members of this group
        active_members = group.members.filter(is_active=True)
        
        for member in active_members:
            # Mark group member as inactive
            member.is_active = False
            member.save(update_fields=['is_active'])
            expired_members_count += 1
            
            # Mark user's course as expired
            user_courses = UserCourse.objects.filter(
                user=member.user,
                course=group.course,
                is_expired=False
            )
            
            for user_course in user_courses:
                user_course.is_expired = True
                user_course.save(update_fields=['is_expired'])
                expired_user_courses_count += 1
    
    return {
        'message': _('Expired groups check completed'),
        'expired_groups': expired_count,
        'expired_members': expired_members_count,
        'expired_user_courses': expired_user_courses_count,
        'check_date': today.isoformat()
    }
