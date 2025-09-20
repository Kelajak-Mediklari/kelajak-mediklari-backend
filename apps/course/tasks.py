from celery import shared_task
from django.utils import timezone
from django.db import transaction
from .models import UserCourse


@shared_task
def check_expired_courses():
    """
    Cron job to check for expired courses and update them
    Runs every hour to check if any course finish_date has passed
    """
    current_time = timezone.now()
    
    with transaction.atomic():
        # Find all UserCourses that have finish_date in the past and are not already marked as expired
        expired_courses = UserCourse.objects.filter(
            finish_date__lt=current_time,
            is_expired=False,
            finish_date__isnull=False
        )
        
        # Update expired courses
        updated_count = expired_courses.update(
            is_expired=True,
            finish_date=None
        )
        
        return f"Updated {updated_count} expired courses"
